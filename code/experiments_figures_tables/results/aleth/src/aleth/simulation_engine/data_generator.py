from __future__ import annotations

import csv
import datetime as dt
import json
import random
import statistics
from typing import Any, Dict, List, Optional

from llm_processor.range_estimator import (
    MONTH_TO_SEASON,
    ModalityProfile,
    Observability,
    Range,
    days_in_month,
    week_bucket_for_day,
)
from model_registry.operators import (
    apply_hw_errors,
    apply_outages,
    apply_precision,
    build_daily_anchor,
    synthesize_measurement,
)


class DataGenerator:
    def synthesize_timeseries(
        self,
        years: List[int],
        day_ranges: Dict[int, Dict[int, Dict[int, Range]]],
        daynight_ranges: Dict[int, Dict[int, Dict[int, Dict[str, Range]]]],
        profile: ModalityProfile,
        freq_minutes: int,
        precision_decimals: int,
        outage_pct: float,
        hw_error_pct: float,
        seed: int,
        obs: Optional[Observability] = None,
    ) -> List[Dict[str, Any]]:
        obs = obs or Observability(enabled=False)
        obs.stage(
            "timeseries_synthesis",
            (
                f"freq_minutes={freq_minutes}, "
                f"precision_decimals={precision_decimals}, "
                f"outage_pct={outage_pct}, "
                f"hw_error_pct={hw_error_pct}"
            ),
        )

        rng = random.Random(seed)
        rows: List[Dict[str, Any]] = []

        total_days = sum(days_in_month(year, month) for year in years for month in range(1, 13))
        processed_days = 0

        for year in years:
            for month in range(1, 13):
                dim = days_in_month(year, month)
                for day in range(1, dim + 1):
                    date_base = dt.datetime(year, month, day)
                    day_r = day_ranges[year][month][day]
                    periods = daynight_ranges[year][month][day]
                    anchor = build_daily_anchor(day_r, month, date_base.timetuple().tm_yday, rng, profile)
                    cur = date_base
                    end = date_base + dt.timedelta(days=1)

                    while cur < end:
                        value = synthesize_measurement(cur, day_r, periods, anchor, rng, profile)
                        rows.append(
                            {
                                "timestamp": cur.isoformat(timespec="minutes"),
                                "year": year,
                                "month": month,
                                "day": day,
                                "week_bucket": week_bucket_for_day(day, dim),
                                "season": MONTH_TO_SEASON[month],
                                "period": "day" if 6 <= cur.hour < 18 else "night",
                                "value": value,
                                "quality_flag": "normal",
                            }
                        )
                        cur += dt.timedelta(minutes=freq_minutes)

                    processed_days += 1
                    if processed_days % 15 == 0 or processed_days == total_days:
                        obs.info(
                            "timeseries_progress",
                            f"processed_days={processed_days}/{total_days}, rows={len(rows)}",
                        )

        obs.stage("post_process_operators", "applying hw_error, outage, precision")
        apply_hw_errors(rows, hw_error_pct=hw_error_pct, rng=rng)
        apply_outages(rows, outage_pct=outage_pct, rng=rng)
        apply_precision(rows, decimals=precision_decimals)

        obs.info(
            "post_process_summary",
            (
                f"rows={len(rows)}, "
                f"hw_error_pct={hw_error_pct}, "
                f"outage_pct={outage_pct}, "
                f"precision_decimals={precision_decimals}"
            ),
        )
        return rows


def write_csv(rows: List[Dict[str, Any]], path: str) -> None:
    fieldnames = [
        "timestamp",
        "year",
        "month",
        "day",
        "week_bucket",
        "season",
        "period",
        "value",
        "quality_flag",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row_out = dict(row)
            if row_out["value"] is None:
                row_out["value"] = ""
            writer.writerow(row_out)


def write_json(data: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def print_summary(rows: List[Dict[str, Any]], unit: str) -> None:
    values = [float(r["value"]) for r in rows if r.get("value") is not None]
    outage_count = sum(1 for r in rows if r.get("value") is None)
    hw_error_count = sum(1 for r in rows if r.get("quality_flag") == "hw_error")

    print(f"Generated {len(rows)} measurements")
    print(f"Available values: {len(values)}")
    print(f"Outage points: {outage_count}")
    print(f"HW-error points: {hw_error_count}")

    if values:
        print(f"Min: {min(values):.3f} {unit}")
        print(f"Max: {max(values):.3f} {unit}")
        print(f"Mean: {statistics.mean(values):.3f} {unit}")
    else:
        print("No non-missing values available for summary statistics")