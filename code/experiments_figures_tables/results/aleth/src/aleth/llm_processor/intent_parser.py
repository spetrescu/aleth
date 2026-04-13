from __future__ import annotations

import dataclasses
import datetime as dt
import json
import re
from typing import Any, Dict, Optional

import requests

from config import MAIN_MODEL_INTENT_PARSING, OLLAMA_TIMEOUT, OLLAMA_URL
from model_registry.operators import (
    get_operator_prompt_fragment,
    normalize_modality,
    validate_granularity_minutes,
    validate_horizon_years,
    validate_percentage,
    validate_precision_decimals,
    resolve_modality,
)


class OllamaError(RuntimeError):
    pass


class IntentOllamaClient:
    def __init__(
        self,
        model: str = MAIN_MODEL_INTENT_PARSING,
        url: str = OLLAMA_URL,
        timeout: int = OLLAMA_TIMEOUT,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout

    def chat_json(self, system: str, user: str, temperature: float = 0.0) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
            },
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        try:
            resp = requests.post(self.url, json=payload, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise OllamaError(
                f"Failed to contact Ollama for intent parsing at {self.url}. Original error: {exc}"
            ) from exc

        data = resp.json()
        try:
            content = data["message"]["content"]
        except Exception as exc:
            raise OllamaError(f"Unexpected Ollama response structure during intent parsing: {data}") from exc

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise OllamaError(f"Intent parser model did not return valid JSON. Raw content:\n{content}")


@dataclasses.dataclass
class ParsedIntent:
    scenario: str
    modality: str
    custom_modality: Optional[str] = None
    unit_hint: Optional[str] = None
    start_year: int = dataclasses.field(default_factory=lambda: dt.date.today().year)
    num_years: int = 1
    freq_minutes: int = 60
    precision_decimals: int = 2
    outage_pct: float = 0.0
    hw_error_pct: float = 0.0
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario,
            "modality": self.modality,
            "custom_modality": self.custom_modality,
            "unit_hint": self.unit_hint,
            "start_year": self.start_year,
            "num_years": self.num_years,
            "freq_minutes": self.freq_minutes,
            "precision_decimals": self.precision_decimals,
            "outage_pct": self.outage_pct,
            "hw_error_pct": self.hw_error_pct,
            "rationale": self.rationale,
        }


class IntentParser:
    def __init__(self, client: Optional[IntentOllamaClient] = None):
        self.client = client or IntentOllamaClient()

    def _build_prompts(
        self,
        scenario: str,
        unit_hint: Optional[str],
        start_year: Optional[int],
        num_years: Optional[int],
        freq_minutes: Optional[int],
    ) -> tuple[str, str]:
        system = f"""
You parse a user's simulation request into a strict JSON object.

You must extract these operator values:
{get_operator_prompt_fragment()}

Rules:
- modality is mandatory
- for known modalities, use one of:
  temperature, humidity, co2, electricity, power, energy, occupancy, pressure, flow
- if the request clearly specifies a telemetry modality that is not in the known list,
  set modality="other" and set custom_modality to the exact cleaned modality name
- if the request does not clearly specify any modality, return null for modality and null for custom_modality
- granularity means sampling interval in minutes
- horizon means number of years to generate
- precision means number of decimal places
- outage means percentage of missing data points
- hw_error means percentage of improbable faulty values
- preserve any unit hint if supplied externally
- keep the cleaned scenario text focused on the building telemetry request
- return strict JSON only

Return schema:
{{
  "scenario": "cleaned user scenario",
  "modality": "temperature|humidity|co2|electricity|power|energy|occupancy|pressure|flow|other|null",
  "custom_modality": "free-text modality name when modality is other, otherwise null",
  "unit_hint": "optional unit or null",
  "start_year": 2025,
  "num_years": 1,
  "freq_minutes": 60,
  "precision_decimals": 2,
  "outage_pct": 0.0,
  "hw_error_pct": 0.0,
  "rationale": "brief explanation"
}}
""".strip()

        user = f"""
Raw user request: {scenario}
External unit hint: {unit_hint}
External start year: {start_year}
External horizon years: {num_years}
External granularity minutes: {freq_minutes}

Task:
Extract the operator configuration from the request.
Use external values when clearly provided, but still infer from the request whenever possible.
If modality is not clearly present, set modality to null.
""".strip()

        return system, user

    def parse(
        self,
        scenario: str,
        unit_hint: Optional[str] = None,
        start_year: Optional[int] = None,
        num_years: Optional[int] = None,
        freq_minutes: Optional[int] = None,
    ) -> ParsedIntent:
        system, user = self._build_prompts(
            scenario=scenario,
            unit_hint=unit_hint,
            start_year=start_year,
            num_years=num_years,
            freq_minutes=freq_minutes,
        )

        try:
            data = self.client.chat_json(system=system, user=user, temperature=0.0)
        except Exception as exc:
            raise OllamaError(f"Intent parsing failed: {exc}") from exc

        modality, custom_modality = resolve_modality(
            data.get("modality"),
            data.get("custom_modality"),
        )

        if modality is None:
            raise ValueError(
                "Simulation rejected: no explicit modality was found in the request. "
                "Please specify a modality such as temperature, humidity, co2, power, energy, occupancy, "
                "or another telemetry type."
            )

        if modality == "other" and not custom_modality:
            raise ValueError(
                "Simulation rejected: the request indicates a non-standard modality, "
                "but its name was not clearly identified."
            )

        resolved_start_year = int(data.get("start_year", start_year or dt.date.today().year))
        resolved_num_years = validate_horizon_years(int(data.get("num_years", num_years or 1)))
        resolved_freq = validate_granularity_minutes(int(data.get("freq_minutes", freq_minutes or 60)))
        resolved_precision = validate_precision_decimals(int(data.get("precision_decimals", 2)))
        resolved_outage = validate_percentage(float(data.get("outage_pct", 0.0)), "outage")
        resolved_hw_error = validate_percentage(float(data.get("hw_error_pct", 0.0)), "hw_error")

        cleaned_scenario = str(data.get("scenario", scenario)).strip() or scenario
        resolved_unit_hint = data.get("unit_hint", unit_hint)
        if resolved_unit_hint is not None:
            resolved_unit_hint = str(resolved_unit_hint).strip() or None

        return ParsedIntent(
            scenario=cleaned_scenario,
            modality=modality,
            custom_modality=custom_modality,
            unit_hint=resolved_unit_hint,
            start_year=resolved_start_year,
            num_years=resolved_num_years,
            freq_minutes=resolved_freq,
            precision_decimals=resolved_precision,
            outage_pct=resolved_outage,
            hw_error_pct=resolved_hw_error,
            rationale=str(data.get("rationale", "")).strip(),
        )