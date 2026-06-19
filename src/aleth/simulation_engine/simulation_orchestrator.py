from __future__ import annotations

from typing import Any, Dict, List, Optional

from llm_processor.intent_parser import IntentParser
from llm_processor.range_estimator import HierarchicalRangeGenerator
from simulation_engine.data_generator import DataGenerator
from simulation_engine.spec_generator import SpecGenerator, hierarchy_to_jsonable


class SimulationOrchestrator:
    def __init__(
        self,
        intent_parser: IntentParser,
        range_estimator: HierarchicalRangeGenerator,
        spec_generator: SpecGenerator,
        data_generator: DataGenerator,
    ):
        self.intent_parser = intent_parser
        self.range_estimator = range_estimator
        self.spec_generator = spec_generator
        self.data_generator = data_generator

    def run(
        self,
        scenario: str,
        years: Optional[List[int]],
        unit_hint: str | None,
        freq_minutes: Optional[int],
        seed: int,
        start_year: Optional[int] = None,
        num_years: Optional[int] = None,
    ) -> Dict[str, Any]:
        intent = self.intent_parser.parse(
            scenario=scenario,
            unit_hint=unit_hint,
            start_year=start_year if start_year is not None else (years[0] if years else None),
            num_years=num_years if num_years is not None else (len(years) if years else None),
            freq_minutes=freq_minutes,
        )

        resolved_years = [intent.start_year + i for i in range(intent.num_years)]

        self.range_estimator.obs.info(
            "simulation_intent",
            (
                f"modality={intent.modality}, "
                f"granularity_minutes={intent.freq_minutes}, "
                f"horizon_years={intent.num_years}, "
                f"precision_decimals={intent.precision_decimals}, "
                f"outage_pct={intent.outage_pct}, "
                f"hw_error_pct={intent.hw_error_pct}"
            ),
        )

        (
            profile,
            year_ranges,
            season_ranges,
            month_ranges,
            week_ranges,
            day_ranges,
            daynight_ranges,
        ) = self.spec_generator.generate_hierarchy(
            generator=self.range_estimator,
            scenario=intent.scenario,
            years=resolved_years,
            unit_hint=intent.unit_hint,
        )

        unit = intent.unit_hint or profile.unit

        rows = self.data_generator.synthesize_timeseries(
            years=resolved_years,
            day_ranges=day_ranges,
            daynight_ranges=daynight_ranges,
            profile=profile,
            freq_minutes=intent.freq_minutes,
            precision_decimals=intent.precision_decimals,
            outage_pct=intent.outage_pct,
            hw_error_pct=intent.hw_error_pct,
            seed=seed,
            obs=self.range_estimator.obs,
        )

        hierarchy_json = hierarchy_to_jsonable(
            resolved_years,
            profile,
            year_ranges,
            season_ranges,
            month_ranges,
            week_ranges,
            day_ranges,
            daynight_ranges,
            intent.scenario,
            unit,
        )

        return {
            "intent": intent,
            "profile": profile,
            "unit": unit,
            "rows": rows,
            "hierarchy_json": hierarchy_json,
            "year_ranges": year_ranges,
            "season_ranges": season_ranges,
            "month_ranges": month_ranges,
            "week_ranges": week_ranges,
            "day_ranges": day_ranges,
            "daynight_ranges": daynight_ranges,
            "years": resolved_years,
        }