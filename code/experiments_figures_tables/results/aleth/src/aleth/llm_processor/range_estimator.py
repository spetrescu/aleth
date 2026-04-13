from __future__ import annotations

import csv
import dataclasses
import datetime as dt
import json
import math
import random
import re
import statistics
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from config import MAIN_MODEL_RANGE_ESTIMATOR, OLLAMA_TIMEOUT, OLLAMA_URL

try:
    from tqdm import tqdm
except Exception:
    tqdm = None


SEASONS = ["winter", "spring", "summer", "autumn"]
MONTH_TO_SEASON = {
    1: "winter",
    2: "winter",
    3: "spring",
    4: "spring",
    5: "spring",
    6: "summer",
    7: "summer",
    8: "summer",
    9: "autumn",
    10: "autumn",
    11: "autumn",
    12: "winter",
}
MONTH_NAMES = {
    1: "january",
    2: "february",
    3: "march",
    4: "april",
    5: "may",
    6: "june",
    7: "july",
    8: "august",
    9: "september",
    10: "october",
    11: "november",
    12: "december",
}


@dataclasses.dataclass
class Range:
    minimum: float
    maximum: float
    rationale: str = ""

    def __post_init__(self) -> None:
        if self.minimum > self.maximum:
            self.minimum, self.maximum = self.maximum, self.minimum

    def clamp_within(self, parent: "Range") -> "Range":
        lo = max(self.minimum, parent.minimum)
        hi = min(self.maximum, parent.maximum)
        if lo > hi:
            center = min(max((self.minimum + self.maximum) / 2.0, parent.minimum), parent.maximum)
            lo = hi = center
        return Range(lo, hi, self.rationale)

    def width(self) -> float:
        return self.maximum - self.minimum

    def midpoint(self) -> float:
        return (self.minimum + self.maximum) / 2.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min": self.minimum,
            "max": self.maximum,
            "rationale": self.rationale,
        }


@dataclasses.dataclass
class ModalityProfile:
    sensor_family: str
    unit: str
    annual_cycle_strength: float
    annual_cycle_phase_day: int
    month_drift_strength: float
    day_night_contrast: float
    short_term_variability: float
    rationale: str = ""

    def normalized(self) -> "ModalityProfile":
        def clamp(x: float, lo: float, hi: float) -> float:
            return min(max(x, lo), hi)

        phase = int(self.annual_cycle_phase_day)
        while phase < 1:
            phase += 365
        while phase > 365:
            phase -= 365

        family = (self.sensor_family or "generic").strip().lower()
        unit = (self.unit or "unit").strip()

        return ModalityProfile(
            sensor_family=family,
            unit=unit,
            annual_cycle_strength=clamp(float(self.annual_cycle_strength), 0.0, 1.0),
            annual_cycle_phase_day=phase,
            month_drift_strength=clamp(float(self.month_drift_strength), 0.0, 1.0),
            day_night_contrast=clamp(float(self.day_night_contrast), 0.0, 1.0),
            short_term_variability=clamp(float(self.short_term_variability), 0.0, 1.0),
            rationale=self.rationale or "",
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_family": self.sensor_family,
            "unit": self.unit,
            "annual_cycle_strength": self.annual_cycle_strength,
            "annual_cycle_phase_day": self.annual_cycle_phase_day,
            "month_drift_strength": self.month_drift_strength,
            "day_night_contrast": self.day_night_contrast,
            "short_term_variability": self.short_term_variability,
            "rationale": self.rationale,
        }


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(
        self,
        model: str = MAIN_MODEL_RANGE_ESTIMATOR,
        url: str = OLLAMA_URL,
        timeout: int = OLLAMA_TIMEOUT,
    ):
        self.model = model
        self.url = url
        self.timeout = timeout

    def chat_json(self, system: str, user: str, temperature: float = 0.2) -> Dict[str, Any]:
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
                f"Failed to contact Ollama at {self.url}. Make sure Ollama is running and the model is available. Original error: {exc}"
            ) from exc

        data = resp.json()
        try:
            content = data["message"]["content"]
        except Exception as exc:
            raise OllamaError(f"Unexpected Ollama response structure: {data}") from exc

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, flags=re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise OllamaError(f"Model did not return valid JSON. Raw content:\n{content}")

class Observability:
    def __init__(
        self,
        enabled: bool = True,
        show_prompts: bool = False,
        event_log_path: Optional[str] = None,
        use_tqdm: bool = False,
    ):
        self.enabled = enabled
        self.show_prompts = show_prompts
        self.event_log_path = event_log_path
        self.use_tqdm = use_tqdm and tqdm is not None

        self.current_stage: str = "init"
        self.total_steps: int = 0
        self.completed_steps: int = 0
        self.stage_started_at: Optional[float] = None
        self.run_started_at: float = time.time()
        self._pbar = None

        self.request_durations_s: List[float] = []
        self.request_cumulative_s: List[float] = []
        self.total_llm_time_s: float = 0.0
        self.llm_request_count: int = 0

    def set_total_steps(self, total: int) -> None:
        self.total_steps = total
        if self.use_tqdm:
            self._pbar = tqdm(total=total, desc="Hierarchy generation", unit="step")

    def close(self) -> None:
        if self._pbar is not None:
            self._pbar.close()

    def _truncate(self, text: str, limit: int = 500) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= limit:
            return text
        return text[: limit - 3] + "..."

    def _emit(self, level: str, event: str, payload: Dict[str, Any]) -> None:
        record = {
            "ts": dt.datetime.now().isoformat(timespec="seconds"),
            "level": level,
            "event": event,
            "stage": self.current_stage,
            "completed_steps": self.completed_steps,
            "total_steps": self.total_steps,
            "progress_pct": round((100.0 * self.completed_steps / self.total_steps), 2) if self.total_steps else None,
            "llm_request_count": self.llm_request_count,
            "total_llm_time_s": round(self.total_llm_time_s, 6),
            **payload,
        }

        if self.enabled:
            msg = f"[{record['ts']}] [{level.upper()}] [{self.current_stage}] {event}"
            extras = []
            if "detail" in payload:
                extras.append(str(payload["detail"]))
            if "duration_s" in payload:
                extras.append(f"duration={payload['duration_s']:.2f}s")
            if "cumulative_llm_time_s" in payload:
                extras.append(f"cum_llm={payload['cumulative_llm_time_s']:.2f}s")
            if self.total_steps:
                extras.append(f"progress={self.completed_steps}/{self.total_steps} ({record['progress_pct']:.2f}%)")
            if extras:
                msg += " | " + " | ".join(extras)
            print(msg, file=sys.stderr)

        if self.event_log_path:
            with open(self.event_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def stage(self, name: str, detail: str = "") -> None:
        self.current_stage = name
        self.stage_started_at = time.time()
        self._emit("info", "stage_start", {"detail": detail})

    def prompt(self, system: str, user: str) -> None:
        payload: Dict[str, Any] = {}
        if self.show_prompts:
            payload["system_prompt_preview"] = self._truncate(system, 700)
            payload["user_prompt_preview"] = self._truncate(user, 1200)
            self._emit("debug", "prompt_preview", payload)

    def llm_attempt(self, attempt: int, max_attempts: int) -> None:
        self._emit("info", "llm_attempt", {"detail": f"attempt {attempt}/{max_attempts}"})

    def llm_success(self, duration_s: float, response_keys: Optional[List[str]] = None) -> None:
        self.llm_request_count += 1
        self.total_llm_time_s += duration_s
        self.request_durations_s.append(duration_s)
        self.request_cumulative_s.append(self.total_llm_time_s)

        payload: Dict[str, Any] = {
            "duration_s": duration_s,
            "request_index": self.llm_request_count,
            "cumulative_llm_time_s": self.total_llm_time_s,
        }
        if response_keys is not None:
            payload["response_keys"] = response_keys
        self._emit("info", "llm_success", payload)

    def llm_retry(self, error: str, sleep_s: float) -> None:
        self._emit("warning", "llm_retry", {"detail": f"{error}; sleeping {sleep_s:.2f}s"})

    def llm_failure(self, error: str) -> None:
        self._emit("error", "llm_failure", {"detail": error})

    def step_done(self, detail: str = "") -> None:
        self.completed_steps += 1
        if self._pbar is not None:
            self._pbar.update(1)
            if detail:
                self._pbar.set_postfix_str(detail[:80])
        self._emit("info", "step_done", {"detail": detail})

    def info(self, event: str, detail: str = "") -> None:
        self._emit("info", event, {"detail": detail})

    def summary(self) -> None:
        total_duration = time.time() - self.run_started_at
        self._emit(
            "info",
            "run_summary",
            {
                "duration_s": total_duration,
                "detail": "generation finished",
                "llm_requests": self.llm_request_count,
                "total_llm_time_s": self.total_llm_time_s,
                "avg_llm_time_s": (
                    self.total_llm_time_s / self.llm_request_count if self.llm_request_count else 0.0
                ),
            },
        )


class HierarchicalRangeGenerator:
    def __init__(
        self,
        client: OllamaClient,
        verbose: bool = False,
        retry_attempts: int = 2,
        observability: Optional[Observability] = None,
    ):
        self.client = client
        self.verbose = verbose
        self.retry_attempts = retry_attempts
        self.obs = observability or Observability(enabled=False)

    def _call_with_retry(self, system: str, user: str) -> Dict[str, Any]:
        last_err: Optional[Exception] = None
        max_attempts = self.retry_attempts + 1
        self.obs.prompt(system, user)

        for attempt in range(max_attempts):
            started = time.time()
            try:
                self.obs.llm_attempt(attempt + 1, max_attempts)
                result = self.client.chat_json(system=system, user=user)
                duration = time.time() - started
                self.obs.llm_success(duration_s=duration, response_keys=sorted(result.keys()))
                if self.verbose:
                    print(json.dumps(result, indent=2), file=sys.stderr)
                return result
            except Exception as exc:
                last_err = exc
                if attempt < self.retry_attempts:
                    sleep_s = 1.2 * (attempt + 1)
                    self.obs.llm_retry(str(exc), sleep_s=sleep_s)
                    time.sleep(sleep_s)
                else:
                    break

        self.obs.llm_failure(str(last_err))
        raise OllamaError(f"LLM call failed after retries: {last_err}")

    def generate_modality_profile(self, scenario: str, unit_hint: Optional[str]) -> ModalityProfile:
        self.obs.stage("modality_profile", "deriving modality behavior")
        system = """
You classify one building telemetry scenario and return a compact modality profile.
The purpose is to keep one unified synthesis logic across different modalities.

You must infer how strong the yearly cycle, month-to-month drift, day/night contrast,
and short-term variability should be for this sensor. Do not design a different
generator for specific modalities. Instead, describe how the SAME generic generator
should behave for this scenario.

Important:
- Electricity, power, and energy sensors may still have an annual cycle, but often weaker
  than temperature unless the scenario strongly implies weather-driven loads.
- Temperature often has stronger annual cycle and moderate to strong day/night contrast.
- CO2 and occupancy may have stronger day/night contrast than annual cycle.
- Return only strict JSON.

Schema:
{
  "sensor_family": "temperature|humidity|co2|electricity|power|energy|occupancy|pressure|flow|generic",
  "unit": "kW",
  "annual_cycle_strength": 0.0,
  "annual_cycle_phase_day": 200,
  "month_drift_strength": 0.0,
  "day_night_contrast": 0.0,
  "short_term_variability": 0.0,
  "rationale": "..."
}

Field meanings:
- annual_cycle_strength: 0..1, strength of yearly cyclical effect
- annual_cycle_phase_day: 1..365, approximate day-of-year where the annual cycle peaks
- month_drift_strength: 0..1, extra slow drift within the year beyond the broad annual cycle
- day_night_contrast: 0..1, how different day and night tend to be
- short_term_variability: 0..1, how noisy / jagged short-term measurements should be
""".strip()

        user = f"""
Scenario: {scenario}
Unit hint: {unit_hint or 'infer from scenario'}

Task:
Infer a modality profile that lets a generic hierarchical generator behave appropriately
for this sensor. Keep the profile plausible and conservative.
""".strip()

        data = self._call_with_retry(system, user)
        resolved_unit = self.resolve_unit(
            scenario=scenario,
            unit_hint=unit_hint,
            llm_unit=data.get("unit"),
        )

        profile = ModalityProfile(
            sensor_family=str(data.get("sensor_family", "generic")),
            unit=resolved_unit,
            annual_cycle_strength=float(data.get("annual_cycle_strength", 0.25)),
            annual_cycle_phase_day=int(data.get("annual_cycle_phase_day", 200)),
            month_drift_strength=float(data.get("month_drift_strength", 0.15)),
            day_night_contrast=float(data.get("day_night_contrast", 0.4)),
            short_term_variability=float(data.get("short_term_variability", 0.2)),
            rationale=str(data.get("rationale", "")),
        ).normalized()

        self.obs.step_done(f"profile family={profile.sensor_family} unit={profile.unit}")
        return profile

    def generate_year_ranges(
        self,
        scenario: str,
        years: List[int],
        unit_hint: Optional[str],
        profile: ModalityProfile,
    ) -> Dict[int, Range]:
        self.obs.stage("year_ranges", f"years={years}")
        system = """
You estimate realistic telemetry ranges for one building sensor.
Assume the scenario is for a single building sensor.
If the user did not provide enough context, assume the building is located in the south of France.
Return only strict JSON.
Be conservative and physically plausible.

Important:
- Use the provided modality profile to shape your expectations.
- Keep the same logic regardless of modality.
- For electricity-like sensors, the annual variation may be weaker than for temperature,
  unless the scenario strongly implies heating/cooling dominated demand.

The output schema is:
{
  "years": [
    {"year": 2025, "min": 0.0, "max": 1.0, "rationale": "..."}
  ]
}
""".strip()

        user = f"""
Scenario: {scenario}
Years to estimate: {years}
Unit hint: {unit_hint or 'infer from scenario'}
Modality profile: {json.dumps(profile.to_dict(), ensure_ascii=False)}

Task:
Estimate one realistic annual min/max range for each year.
These are the full-year extremes for that sensor.
Values must be numeric.
Keep each year's range plausible for that specific sensor and building scenario.
Use the modality profile as guidance for how broad and seasonally structured the sensor should be.
""".strip()
        data = self._call_with_retry(system, user)
        result: Dict[int, Range] = {}
        for item in data.get("years", []):
            y = int(item["year"])
            result[y] = Range(float(item["min"]), float(item["max"]), str(item.get("rationale", "")))
        missing = [y for y in years if y not in result]
        if missing:
            raise OllamaError(f"Model omitted year ranges for: {missing}")
        self.obs.step_done(f"generated {len(result)} year ranges")
        return result

    def generate_season_ranges(
        self,
        scenario: str,
        year: int,
        year_range: Range,
        unit_hint: Optional[str],
        profile: ModalityProfile,
    ) -> Dict[str, Range]:
        self.obs.stage("season_ranges", f"year={year}")
        system = """
You estimate realistic seasonal ranges for one building sensor.
Assume the building is in the south of France when details are missing.
You must keep all seasonal ranges inside the given annual range.
Return only strict JSON.

Important:
- Use the provided modality profile.
- Preserve a unified generic logic across modalities.
- If the profile implies weak annual cycle, then keep seasonal differences correspondingly modest.
- If the profile implies strong annual cycle, then stronger seasonal contrast is acceptable.

Schema:
{
  "seasons": [
    {"season": "winter", "min": 0.0, "max": 1.0, "rationale": "..."},
    {"season": "spring", "min": 0.0, "max": 1.0, "rationale": "..."},
    {"season": "summer", "min": 0.0, "max": 1.0, "rationale": "..."},
    {"season": "autumn", "min": 0.0, "max": 1.0, "rationale": "..."}
  ]
}
""".strip()
        user = f"""
Scenario: {scenario}
Year: {year}
Annual min/max: {year_range.to_dict()}
Unit hint: {unit_hint or 'infer from scenario'}
Modality profile: {json.dumps(profile.to_dict(), ensure_ascii=False)}

Task:
Estimate realistic min/max ranges for winter, spring, summer, autumn.
Every seasonal range must stay within the annual range.
Seasonality should make sense for the sensor and should align with the modality profile.
""".strip()
        data = self._call_with_retry(system, user)
        out: Dict[str, Range] = {}
        for item in data.get("seasons", []):
            s = str(item["season"]).strip().lower()
            if s in SEASONS:
                out[s] = Range(float(item["min"]), float(item["max"]), str(item.get("rationale", ""))).clamp_within(year_range)
        for s in SEASONS:
            if s not in out:
                out[s] = self._fallback_child_range(year_range, shrink=0.08)
        self.obs.step_done(f"year={year} seasons={len(out)}")
        return out

    def generate_month_ranges(
        self,
        scenario: str,
        year: int,
        season: str,
        season_range: Range,
        unit_hint: Optional[str],
        profile: ModalityProfile,
    ) -> Dict[int, Range]:
        months = [m for m, s in MONTH_TO_SEASON.items() if s == season]
        self.obs.stage("month_ranges", f"year={year} season={season} months={months}")
        system = """
You estimate realistic monthly ranges for one building sensor.
Assume south of France if underspecified.
All month ranges must stay inside the given seasonal range.
Return only strict JSON.

Important:
- Use the provided modality profile.
- Keep the same general hierarchical logic for all modalities.
- Reflect gradual progression across the season.
- If annual and monthly drift are weak according to the profile, keep adjacent months closer together.

Schema:
{
  "months": [
    {"month": 1, "name": "january", "min": 0.0, "max": 1.0, "rationale": "..."}
  ]
}
""".strip()
        user = f"""
Scenario: {scenario}
Year: {year}
Season: {season}
Months in season: {months}
Seasonal min/max: {season_range.to_dict()}
Unit hint: {unit_hint or 'infer from scenario'}
Modality profile: {json.dumps(profile.to_dict(), ensure_ascii=False)}

Task:
Estimate monthly min/max ranges for the months in this season.
Each monthly range must be inside the seasonal range.
Reflect gradual progression across the season and align with the modality profile.
""".strip()
        data = self._call_with_retry(system, user)
        out: Dict[int, Range] = {}
        for item in data.get("months", []):
            m = int(item["month"])
            if m in months:
                out[m] = Range(float(item["min"]), float(item["max"]), str(item.get("rationale", ""))).clamp_within(season_range)
        for m in months:
            if m not in out:
                out[m] = self._fallback_child_range(season_range, shrink=0.1)
        self.obs.step_done(f"year={year} season={season} months={len(out)}")
        return out

    def generate_week_ranges(
        self,
        scenario: str,
        year: int,
        month: int,
        month_range: Range,
        unit_hint: Optional[str],
        profile: ModalityProfile,
    ) -> Dict[int, Range]:
        self.obs.stage("week_ranges", f"year={year} month={month}")
        system = """
You estimate realistic weekly ranges for one building sensor.
Weeks are 1..4 buckets inside the month.
All weekly ranges must stay inside the monthly range.
Assume south of France if underspecified.
Return only strict JSON.

Important:
- Use the provided modality profile.
- Weekly movement should be conservative unless the scenario implies substantial short-term variation.
- Keep the same generic hierarchy across modalities.

Schema:
{
  "weeks": [
    {"week": 1, "min": 0.0, "max": 1.0, "rationale": "..."},
    {"week": 2, "min": 0.0, "max": 1.0, "rationale": "..."},
    {"week": 3, "min": 0.0, "max": 1.0, "rationale": "..."},
    {"week": 4, "min": 0.0, "max": 1.0, "rationale": "..."}
  ]
}
""".strip()
        user = f"""
Scenario: {scenario}
Year: {year}
Month: {month} ({MONTH_NAMES[month]})
Monthly min/max: {month_range.to_dict()}
Unit hint: {unit_hint or 'infer from scenario'}
Modality profile: {json.dumps(profile.to_dict(), ensure_ascii=False)}

Task:
Estimate min/max ranges for week buckets 1,2,3,4 in this month.
These are not ISO weeks; they are the 4 within-month buckets.
Each weekly range must stay inside the monthly range.
""".strip()
        data = self._call_with_retry(system, user)
        out: Dict[int, Range] = {}
        for item in data.get("weeks", []):
            w = int(item["week"])
            if 1 <= w <= 4:
                out[w] = Range(float(item["min"]), float(item["max"]), str(item.get("rationale", ""))).clamp_within(month_range)
        for w in range(1, 5):
            if w not in out:
                out[w] = self._fallback_child_range(month_range, shrink=0.12)
        self.obs.step_done(f"year={year} month={month} weeks={len(out)}")
        return out

    def generate_day_ranges(
        self,
        scenario: str,
        year: int,
        month: int,
        week: int,
        day_numbers: List[int],
        week_range: Range,
        unit_hint: Optional[str],
        profile: ModalityProfile,
    ) -> Dict[int, Range]:
        self.obs.stage("day_ranges", f"year={year} month={month} week_bucket={week} days={day_numbers}")
        system = """
You estimate realistic daily ranges for one building sensor.
All daily ranges must stay inside the given weekly range.
Assume south of France if underspecified.
Return only strict JSON.

Important:
- Use the provided modality profile.
- Allow mild day-to-day variability by default.
- Increase day-to-day differences only if the scenario and profile justify it.
- Keep the same generic hierarchy for all modalities.

Schema:
{
  "days": [
    {"day": 1, "min": 0.0, "max": 1.0, "rationale": "..."}
  ]
}
""".strip()
        user = f"""
Scenario: {scenario}
Year: {year}
Month: {month} ({MONTH_NAMES[month]})
Week bucket: {week}
Days in this bucket: {day_numbers}
Weekly min/max: {week_range.to_dict()}
Unit hint: {unit_hint or 'infer from scenario'}
Modality profile: {json.dumps(profile.to_dict(), ensure_ascii=False)}

Task:
Estimate min/max ranges for each listed day of month.
Each daily range must stay inside the weekly range.
Allow mild day-to-day variability consistent with the modality profile.
""".strip()
        data = self._call_with_retry(system, user)
        out: Dict[int, Range] = {}
        allowed = set(day_numbers)
        for item in data.get("days", []):
            d = int(item["day"])
            if d in allowed:
                out[d] = Range(float(item["min"]), float(item["max"]), str(item.get("rationale", ""))).clamp_within(week_range)
        for d in day_numbers:
            if d not in out:
                out[d] = self._fallback_child_range(week_range, shrink=0.15)
        self.obs.step_done(f"year={year} month={month} week_bucket={week} days={len(out)}")
        return out

    def generate_day_night_ranges(
        self,
        scenario: str,
        year: int,
        month: int,
        day: int,
        day_range: Range,
        unit_hint: Optional[str],
        profile: ModalityProfile,
    ) -> Dict[str, Range]:
        self.obs.stage("day_night_ranges", f"date={year}-{month:02d}-{day:02d}")
        system = """
You estimate daytime and nighttime ranges for one building sensor.
Both ranges must stay inside the given daily range.
Assume south of France if underspecified.
Return only strict JSON.

Important:
- Use the provided modality profile.
- Preserve the same day/night structure across modalities.
- If the profile implies weak day/night contrast, keep day and night closer together.
- If the profile implies strong day/night contrast, day and night may differ more.
- The two periods may overlap.

Schema:
{
  "periods": [
    {"period": "day", "min": 0.0, "max": 1.0, "rationale": "..."},
    {"period": "night", "min": 0.0, "max": 1.0, "rationale": "..."}
  ]
}
""".strip()
        user = f"""
Scenario: {scenario}
Date: {year}-{month:02d}-{day:02d}
Daily min/max: {day_range.to_dict()}
Unit hint: {unit_hint or 'infer from scenario'}
Modality profile: {json.dumps(profile.to_dict(), ensure_ascii=False)}

Task:
Estimate one min/max range for daytime and one for nighttime.
Both must stay inside the daily range.
The two periods may overlap, but should reflect realistic diurnal behavior for this modality.
""".strip()
        data = self._call_with_retry(system, user)
        out: Dict[str, Range] = {}
        for item in data.get("periods", []):
            p = str(item["period"]).strip().lower()
            if p in {"day", "night"}:
                out[p] = Range(float(item["min"]), float(item["max"]), str(item.get("rationale", ""))).clamp_within(day_range)
        if "day" not in out:
            out["day"] = self._fallback_child_range(day_range, shrink=0.12)
        if "night" not in out:
            out["night"] = self._fallback_child_range(day_range, shrink=0.12)
        self.obs.step_done(f"date={year}-{month:02d}-{day:02d}")
        return out

    @staticmethod
    def _fallback_child_range(parent: Range, shrink: float = 0.1) -> Range:
        width = max(parent.width(), 1e-9)
        new_width = width * (1.0 - shrink)
        center = parent.midpoint()
        lo = max(parent.minimum, center - new_width / 2.0)
        hi = min(parent.maximum, center + new_width / 2.0)
        return Range(lo, hi, "Fallback range derived from parent")
    
    def resolve_unit(
        self,
        scenario: str,
        unit_hint: Optional[str] = None,
        llm_unit: Optional[str] = None,
    ) -> str:
        if unit_hint and str(unit_hint).strip():
            return str(unit_hint).strip()

        hardcoded = infer_unit_from_scenario(scenario)
        if hardcoded:
            return hardcoded

        if llm_unit and str(llm_unit).strip():
            return str(llm_unit).strip()

        inferred = self.infer_unit_with_llm(scenario=scenario, unit_hint=unit_hint)
        if inferred:
            return inferred

        return "unit"

def infer_unit_from_scenario(scenario: str) -> Optional[str]:
    s = scenario.lower()
    if "temperature" in s or "temp" in s:
        return "°C"
    if "humidity" in s:
        return "%RH"
    if "co2" in s or "carbon dioxide" in s:
        return "ppm"
    if "power" in s:
        return "kW"
    if "energy" in s:
        return "kWh"
    if "electricity" in s or "electric" in s:
        return "kW"
    if "pressure" in s:
        return "Pa"
    if "occup" in s or "people count" in s:
        return "count"
    if "flow" in s:
        return "m3/s"
    return None

def infer_unit_with_llm(self, scenario: str, unit_hint: Optional[str] = None) -> Optional[str]:
    system = """
You infer the most plausible measurement unit for one building telemetry modality.

Rules:
- Return strict JSON only.
- Prefer the externally supplied unit hint if it is already plausible.
- If the scenario clearly implies a standard unit, return it.
- If multiple units are plausible and there is not enough context, return null.
- Do not guess a specific unit when confidence is low.
- Examples:
temperature -> °C
humidity -> %RH
co2 -> ppm
power -> kW
energy -> kWh
occupancy -> count
pressure -> Pa
flow -> m3/s or null if unclear
voc -> ppb or ppm depending on context, otherwise null

Schema:
{
"unit": "string or null",
"confidence": "high|medium|low",
"rationale": "brief explanation"
}
""".strip()

    user = f"""
Scenario: {scenario}
External unit hint: {unit_hint or 'none'}

Task:
Infer the most plausible measurement unit for the telemetry described in the scenario.
If the correct unit cannot be determined confidently, return null.
""".strip()

    data = self._call_with_retry(system, user)

    unit = data.get("unit")
    if unit is None:
        return None

    unit = str(unit).strip()
    if not unit or unit.lower() == "null":
        return None

    confidence = str(data.get("confidence", "")).strip().lower()
    if confidence == "low":
        return None

    return unit

def days_in_month(year: int, month: int) -> int:
    if month == 12:
        nxt = dt.date(year + 1, 1, 1)
    else:
        nxt = dt.date(year, month + 1, 1)
    cur = dt.date(year, month, 1)
    return (nxt - cur).days


def week_bucket_for_day(day: int, dim: int) -> int:
    edges = [1, math.ceil(dim / 4), math.ceil(dim / 2), math.ceil(3 * dim / 4), dim]
    if day <= edges[1]:
        return 1
    if day <= edges[2]:
        return 2
    if day <= edges[3]:
        return 3
    return 4


def day_numbers_for_bucket(year: int, month: int, week_bucket: int) -> List[int]:
    dim = days_in_month(year, month)
    return [d for d in range(1, dim + 1) if week_bucket_for_day(d, dim) == week_bucket]



def estimate_total_hierarchy_steps(years: List[int]) -> int:
    total = 0
    total += 1
    for year in years:
        total += 1
        total += 1
        total += 4
        total += 12
        for month in range(1, 13):
            total += 4
            total += days_in_month(year, month)
    return total
