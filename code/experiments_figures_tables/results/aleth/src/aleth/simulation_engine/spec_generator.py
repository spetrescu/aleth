from __future__ import annotations

from typing import Any, Dict, List, Tuple

from llm_processor.range_estimator import (
    HierarchicalRangeGenerator,
    ModalityProfile,
    MONTH_TO_SEASON,
    Range,
    SEASONS,
    day_numbers_for_bucket,
    days_in_month,
    week_bucket_for_day,
)


class SpecGenerator:
    def generate_hierarchy(
        self,
        generator: HierarchicalRangeGenerator,
        scenario: str,
        years: List[int],
        unit_hint: str | None,
    ) -> Tuple[
        ModalityProfile,
        Dict[int, Range],
        Dict[int, Dict[str, Range]],
        Dict[int, Dict[int, Range]],
        Dict[int, Dict[int, Dict[int, Range]]],
        Dict[int, Dict[int, Dict[int, Range]]],
        Dict[int, Dict[int, Dict[int, Dict[str, Range]]]],
    ]:
        profile = generator.generate_modality_profile(scenario, unit_hint)
        year_ranges = generator.generate_year_ranges(scenario, years, unit_hint, profile)
        season_ranges: Dict[int, Dict[str, Range]] = {}
        month_ranges: Dict[int, Dict[int, Range]] = {}
        week_ranges: Dict[int, Dict[int, Dict[int, Range]]] = {}
        day_ranges: Dict[int, Dict[int, Dict[int, Range]]] = {}
        daynight_ranges: Dict[int, Dict[int, Dict[int, Dict[str, Range]]]] = {}

        for year in years:
            season_ranges[year] = generator.generate_season_ranges(scenario, year, year_ranges[year], unit_hint, profile)
            month_ranges[year] = {}
            week_ranges[year] = {}
            day_ranges[year] = {}
            daynight_ranges[year] = {}

            for season in SEASONS:
                months = generator.generate_month_ranges(scenario, year, season, season_ranges[year][season], unit_hint, profile)
                month_ranges[year].update(months)

            for month in range(1, 13):
                week_ranges[year][month] = generator.generate_week_ranges(scenario, year, month, month_ranges[year][month], unit_hint, profile)
                day_ranges[year][month] = {}
                daynight_ranges[year][month] = {}
                for wb in range(1, 5):
                    bucket_days = day_numbers_for_bucket(year, month, wb)
                    if not bucket_days:
                        continue
                    d_ranges = generator.generate_day_ranges(
                        scenario,
                        year,
                        month,
                        wb,
                        bucket_days,
                        week_ranges[year][month][wb],
                        unit_hint,
                        profile,
                    )
                    day_ranges[year][month].update(d_ranges)
                for day in range(1, days_in_month(year, month) + 1):
                    daynight_ranges[year][month][day] = generator.generate_day_night_ranges(
                        scenario,
                        year,
                        month,
                        day,
                        day_ranges[year][month][day],
                        unit_hint,
                        profile,
                    )

        ensure_nested_consistency(year_ranges, season_ranges, month_ranges, week_ranges, day_ranges, daynight_ranges)
        return profile, year_ranges, season_ranges, month_ranges, week_ranges, day_ranges, daynight_ranges


def ensure_nested_consistency(
    year_ranges: Dict[int, Range],
    season_ranges: Dict[int, Dict[str, Range]],
    month_ranges: Dict[int, Dict[int, Range]],
    week_ranges: Dict[int, Dict[int, Dict[int, Range]]],
    day_ranges: Dict[int, Dict[int, Dict[int, Range]]],
    daynight_ranges: Dict[int, Dict[int, Dict[int, Dict[str, Range]]]],
) -> None:
    for year, yr in year_ranges.items():
        for season, sr in season_ranges[year].items():
            season_ranges[year][season] = sr.clamp_within(yr)
        for month, mr in month_ranges[year].items():
            month_ranges[year][month] = mr.clamp_within(season_ranges[year][MONTH_TO_SEASON[month]])
        for month, weeks in week_ranges[year].items():
            for w, wr in weeks.items():
                week_ranges[year][month][w] = wr.clamp_within(month_ranges[year][month])
        for month, days in day_ranges[year].items():
            dim = days_in_month(year, month)
            for d, dr in days.items():
                w = week_bucket_for_day(d, dim)
                day_ranges[year][month][d] = dr.clamp_within(week_ranges[year][month][w])
        for month, days in daynight_ranges[year].items():
            for d, periods in days.items():
                parent = day_ranges[year][month][d]
                for p in ("day", "night"):
                    daynight_ranges[year][month][d][p] = periods[p].clamp_within(parent)


def hierarchy_to_jsonable(
    years: List[int],
    profile: ModalityProfile,
    year_ranges: Dict[int, Range],
    season_ranges: Dict[int, Dict[str, Range]],
    month_ranges: Dict[int, Dict[int, Range]],
    week_ranges: Dict[int, Dict[int, Dict[int, Range]]],
    day_ranges: Dict[int, Dict[int, Dict[int, Range]]],
    daynight_ranges: Dict[int, Dict[int, Dict[int, Dict[str, Range]]]],
    scenario: str,
    unit: str,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "scenario": scenario,
        "unit": unit,
        "modality_profile": profile.to_dict(),
        "years": {},
    }
    for year in years:
        out["years"][str(year)] = {
            "year_range": year_ranges[year].to_dict(),
            "season_ranges": {k: v.to_dict() for k, v in season_ranges[year].items()},
            "month_ranges": {str(k): v.to_dict() for k, v in month_ranges[year].items()},
            "week_ranges": {
                str(month): {str(w): wr.to_dict() for w, wr in week_ranges[year][month].items()}
                for month in week_ranges[year]
            },
            "day_ranges": {
                str(month): {str(day): dr.to_dict() for day, dr in day_ranges[year][month].items()}
                for month in day_ranges[year]
            },
            "day_night_ranges": {
                str(month): {
                    str(day): {period: pr.to_dict() for period, pr in periods.items()}
                    for day, periods in daynight_ranges[year][month].items()
                }
                for month in daynight_ranges[year]
            },
        }
    return out
