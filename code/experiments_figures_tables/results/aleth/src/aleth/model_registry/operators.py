from __future__ import annotations

import dataclasses
import datetime as dt
import math
import random
import re
from typing import Any, Dict, List, Optional, Tuple

from llm_processor.range_estimator import ModalityProfile, Range

# these are some default values for common modalities, however, if the requested modality is not in this list, we use other as type and custom_modality, ultimately inferring unit using infer_unit_with_llm
DEFAULT_SUPPORTED_MODALITIES = {
    "temperature",
    "humidity",
    "co2",
    "electricity",
    "power",
    "energy",
    "pressure",
    "flow",
}

MODALITY_ALIASES = {
    "temp": "temperature",
    "carbon dioxide": "co2",
    "electric": "electricity",
}


@dataclasses.dataclass(frozen=True)
class OperatorDefinition:
    name: str
    description: str
    required: bool
    default: Any
    example_values: List[Any]


def get_operator_definitions() -> List[OperatorDefinition]:
    return [
        OperatorDefinition(
            name="modality",
            description=(
                "Sensor modality to simulate. This is required. "
                "Use a canonical known modality when possible; otherwise use 'other' "
                "and provide the actual free-text modality name separately."
            ),
            required=True,
            default=None,
            example_values=["temperature", "co2", "power", "humidity", "other"],
        ),
        OperatorDefinition(
            name="granularity",
            description="Sampling interval in minutes.",
            required=False,
            default=60,
            example_values=[1, 5, 15, 30, 60],
        ),
        OperatorDefinition(
            name="horizon",
            description="Number of years to simulate.",
            required=False,
            default=1,
            example_values=[1, 2, 3],
        ),
        OperatorDefinition(
            name="precision",
            description="Number of decimal places for generated values.",
            required=False,
            default=2,
            example_values=[0, 1, 2, 3],
        ),
        OperatorDefinition(
            name="outage",
            description="Percentage of points that should be missing at the end of generation.",
            required=False,
            default=0.0,
            example_values=[0.0, 0.5, 1.0, 5.0],
        ),
        OperatorDefinition(
            name="hw_error",
            description="Percentage of points that should contain implausible faulty values.",
            required=False,
            default=0.0,
            example_values=[0.0, 0.5, 1.0, 3.0],
        ),
        OperatorDefinition(
            name="speed",
            description=(
                "Hierarchical generation speed. 'full' issues one LLM call per day for the "
                "day/night ranges, 'weekly' batches those ranges across each week-bucket, "
                "'monthly' batches them across the whole month. Batching only changes how "
                "many prompts are sent; per-day day/night granularity is preserved."
            ),
            required=False,
            default="full",
            example_values=["full", "weekly", "monthly"],
        ),
        OperatorDefinition(
            name="user_range",
            description=(
                "Explicit numeric value bounds for the sensor when the user states them. "
                "Parse phrases like 'between X and Y', 'from X to Y', 'X to Y', 'X-Y <unit>' "
                "into {\"min\": X, \"max\": Y}. Strip units; return numbers in the same unit "
                "as unit_hint. Return null if no range is stated, or if only one bound is "
                "given (for example 'below 30', 'above 10'). When provided, this range "
                "becomes the root of the hierarchy and the year-level LLM call is skipped; "
                "all downstream ranges are clamped inside it."
            ),
            required=False,
            default=None,
            example_values=[{"min": 22.0, "max": 25.0}, {"min": 0.0, "max": 100.0}, None],
        ),
    ]


SPEED_OPTIONS = {"full", "weekly", "monthly"}


def validate_speed(value: Optional[str]) -> str:
    if value is None:
        return "full"
    v = str(value).strip().lower()
    if v not in SPEED_OPTIONS:
        return "full"
    return v


def validate_user_range(value: Any) -> Tuple[Optional[float], Optional[float]]:
    if not isinstance(value, dict):
        return None, None
    lo = value.get("min")
    hi = value.get("max")
    if lo is None or hi is None:
        return None, None
    try:
        lo_f = float(lo)
        hi_f = float(hi)
    except (TypeError, ValueError):
        return None, None
    if lo_f > hi_f:
        lo_f, hi_f = hi_f, lo_f
    return lo_f, hi_f


def get_operator_prompt_fragment() -> str:
    lines = []
    for op in get_operator_definitions():
        lines.append(
            f"- {op.name}: required={str(op.required).lower()}, default={op.default!r}, "
            f"description={op.description}, examples={op.example_values}"
        )
    return "\n".join(lines)


def _clean_modality_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text or None


def resolve_modality(
    modality_value: Optional[str],
    custom_modality_value: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    modality = _clean_modality_text(modality_value)
    custom = _clean_modality_text(custom_modality_value)

    if modality is None:
        return None, None

    modality = MODALITY_ALIASES.get(modality, modality)

    if modality in DEFAULT_SUPPORTED_MODALITIES:
        return modality, None

    if modality == "other":
        if custom:
            custom = MODALITY_ALIASES.get(custom, custom)
            if custom in DEFAULT_SUPPORTED_MODALITIES:
                return custom, None
            return "other", custom
        return "other", None

    if modality:
        return "other", modality

    return None, None

def normalize_modality(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    modality = str(value).strip().lower()
    if modality in DEFAULT_SUPPORTED_MODALITIES:
        return modality
    aliases = {
        "temp": "temperature",
        "carbon dioxide": "co2",
        "electric": "electricity",
    }
    modality = aliases.get(modality, modality)
    return modality if modality in DEFAULT_SUPPORTED_MODALITIES else None


def validate_granularity_minutes(value: int) -> int:
    if value < 1 or 1440 % value != 0:
        raise ValueError("granularity must be a positive divisor of 1440, e.g. 1, 5, 10, 15, 30, 60")
    return value


def validate_horizon_years(value: int) -> int:
    if value < 1:
        raise ValueError("horizon must be >= 1 year")
    return value


def validate_precision_decimals(value: int) -> int:
    if value < 0 or value > 10:
        raise ValueError("precision must be between 0 and 10")
    return value


def validate_percentage(value: float, name: str) -> float:
    if value < 0.0 or value > 100.0:
        raise ValueError(f"{name} must be between 0 and 100")
    return value


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def gaussian_sample_clipped(rng: random.Random, mean: float, sigma: float, lo: float, hi: float) -> float:
    for _ in range(12):
        x = rng.gauss(mean, sigma)
        if lo <= x <= hi:
            return x
    return min(max(mean, lo), hi)


def annual_cycle_value(day_of_year: int, profile: ModalityProfile) -> float:
    phase = float(profile.annual_cycle_phase_day)
    x = 2.0 * math.pi * ((day_of_year - phase) / 365.25)
    return math.cos(x)


def diurnal_blend(hour: float, contrast_strength: float, sunrise_hour: float = 6.0, sunset_hour: float = 18.0) -> float:
    if sunrise_hour <= hour <= sunset_hour:
        span = sunset_hour - sunrise_hour
        x = (hour - sunrise_hour) / max(span, 1e-9)
        base = math.sin(math.pi * x)
    else:
        base = 0.0
    return lerp(0.5, base, contrast_strength)


def build_daily_anchor(
    day_range: Range,
    month_index: int,
    day_of_year: int,
    rng: random.Random,
    profile: ModalityProfile,
) -> float:
    annual_wave = annual_cycle_value(day_of_year, profile)
    annual_drift = profile.annual_cycle_strength * 0.18 * day_range.width() * annual_wave

    month_wave = math.sin(2 * math.pi * (month_index / 12.0))
    month_drift = profile.month_drift_strength * 0.10 * day_range.width() * month_wave

    base = day_range.midpoint() + annual_drift + month_drift
    sigma = max(day_range.width() * (0.05 + 0.08 * profile.short_term_variability), 1e-6)
    return gaussian_sample_clipped(rng, base, sigma, day_range.minimum, day_range.maximum)


def synthesize_measurement(
    timestamp: dt.datetime,
    day_range: Range,
    period_ranges: Dict[str, Range],
    daily_anchor_value: float,
    rng: random.Random,
    profile: ModalityProfile,
) -> float:
    hour = timestamp.hour + timestamp.minute / 60.0
    alpha = diurnal_blend(hour, contrast_strength=profile.day_night_contrast)

    night_r = period_ranges["night"]
    day_r = period_ranges["day"]

    lo = lerp(night_r.minimum, day_r.minimum, alpha)
    hi = lerp(night_r.maximum, day_r.maximum, alpha)
    if lo > hi:
        lo, hi = hi, lo

    center = lerp(night_r.midpoint(), day_r.midpoint(), alpha)
    center = 0.65 * center + 0.35 * daily_anchor_value

    variability_scale = 0.45 + 1.10 * profile.short_term_variability
    sigma = max((hi - lo) / 8.0 * variability_scale, 1e-6)
    value = gaussian_sample_clipped(rng, center, sigma, lo, hi)

    minute_phase = (timestamp.hour * 60 + timestamp.minute) / (24 * 60)
    wobble_strength = 0.01 + 0.04 * profile.short_term_variability
    value += wobble_strength * day_range.width() * math.sin(2 * math.pi * minute_phase)
    value = min(max(value, lo), hi)
    value = min(max(value, day_range.minimum), day_range.maximum)
    return value


def apply_hw_errors(
    rows: List[Dict[str, Any]],
    hw_error_pct: float,
    rng: random.Random,
) -> None:
    if hw_error_pct <= 0.0 or not rows:
        return

    candidate_indices = [i for i, row in enumerate(rows) if row.get("value") is not None]
    if not candidate_indices:
        return

    n = min(len(candidate_indices), int(round(len(candidate_indices) * hw_error_pct / 100.0)))
    if n <= 0:
        return

    selected = rng.sample(candidate_indices, n)
    for idx in selected:
        row = rows[idx]
        value = float(row["value"])
        magnitude = max(abs(value), 1.0)

        if rng.random() < 0.5:
            faulty = value + magnitude * (2.5 + 2.0 * rng.random())
        else:
            faulty = value - magnitude * (2.5 + 2.0 * rng.random())

        row["value"] = faulty
        row["quality_flag"] = "hw_error"


def apply_outages(
    rows: List[Dict[str, Any]],
    outage_pct: float,
    rng: random.Random,
) -> None:
    if outage_pct <= 0.0 or not rows:
        return

    candidate_indices = [i for i, row in enumerate(rows) if row.get("value") is not None]
    if not candidate_indices:
        return

    n = min(len(candidate_indices), int(round(len(candidate_indices) * outage_pct / 100.0)))
    if n <= 0:
        return

    selected = rng.sample(candidate_indices, n)
    for idx in selected:
        rows[idx]["value"] = None
        rows[idx]["quality_flag"] = "outage"


def apply_precision(
    rows: List[Dict[str, Any]],
    decimals: int,
) -> None:
    for row in rows:
        if row.get("value") is not None:
            row["value"] = round(float(row["value"]), decimals)
