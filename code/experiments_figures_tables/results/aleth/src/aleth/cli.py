from __future__ import annotations

import argparse
import datetime as dt
import statistics
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
from config import OLLAMA_URL

from llm_processor import (
    IntentParser,
    Observability,
    OllamaClient,
    estimate_total_hierarchy_steps,
    infer_unit_from_scenario,
)
from llm_processor.intent_parser import IntentOllamaClient
from llm_processor.range_estimator import HierarchicalRangeGenerator
from model_registry.stream_examples import get_stream_examples
from simulation_engine import (
    DataGenerator,
    SimulationOrchestrator,
    SpecGenerator,
    print_summary,
    write_csv,
    write_json,
)

from config import MAIN_MODEL_INTENT_PARSING, MAIN_MODEL_RANGE_ESTIMATOR


def plot_timeseries(
    rows: List[Dict[str, Any]],
    unit: str,
    scenario: str,
    output_path: str,
    max_points: int = 5000,
) -> None:
    timestamps = [dt.datetime.fromisoformat(str(r["timestamp"])) for r in rows]
    values = [float(r["value"]) for r in rows]

    if len(values) > max_points:
        step = max(1, len(values) // max_points)
        timestamps = timestamps[::step]
        values = values[::step]

    plt.figure(figsize=(6, 5))
    plt.plot(timestamps, values, linewidth=0.8)
    plt.title(f"Generated telemetry timeseries\n{scenario}")
    plt.xlabel("Timestamp")
    plt.ylabel(f"Value ({unit})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_daily_mean(
    rows: List[Dict[str, Any]],
    unit: str,
    scenario: str,
    output_path: str,
) -> None:
    daily: Dict[dt.date, List[float]] = {}

    for row in rows:
        ts = dt.datetime.fromisoformat(str(row["timestamp"]))
        daily.setdefault(ts.date(), []).append(float(row["value"]))

    dates = sorted(daily.keys())
    means = [statistics.mean(daily[d]) for d in dates]

    plt.figure(figsize=(6, 5))
    plt.plot(dates, means, linewidth=1.2)
    plt.title(f"Daily Mean Telemetry\n{scenario}")
    plt.xlabel("Date")
    plt.ylabel(f"Daily Mean ({unit})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_request_durations(
    obs: Observability,
    scenario: str,
    output_path: str,
) -> bool:
    if not obs.request_durations_s:
        return False

    x = list(range(1, len(obs.request_durations_s) + 1))
    y = obs.request_durations_s

    plt.figure(figsize=(6, 5))
    plt.plot(x, y, marker="o", linewidth=1.0, markersize=3)
    plt.title(f"LLM Request time per request\n{scenario}")
    plt.xlabel("Request index")
    plt.ylabel("Duration (s)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return True


def plot_cumulative_request_time(
    obs: Observability,
    scenario: str,
    output_path: str,
) -> bool:
    if not obs.request_cumulative_s:
        return False

    x = list(range(1, len(obs.request_cumulative_s) + 1))
    y = obs.request_cumulative_s

    plt.figure(figsize=(6, 5))
    plt.plot(x, y, marker="o", linewidth=1.2, markersize=3)
    plt.title(f"Cumulative LLM request time\n{scenario}")
    plt.xlabel("Request index")
    plt.ylabel("Cumulative time (s)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return True


def build_run_paths(results_dir: str, run_timestamp: str) -> Dict[str, Path]:
    run_dir = Path(results_dir) / run_timestamp
    return {
        "run_dir": run_dir,
        "csv": run_dir / "telemetry.csv",
        "ranges_json": run_dir / "ranges.json",
        "timeseries_plot": run_dir / "telemetry_timeseries.png",
        "daily_plot": run_dir / "telemetry_daily_mean.png",
        "request_time_plot": run_dir / "telemetry_request_time.png",
        "request_cumulative_plot": run_dir / "telemetry_request_cumulative_time.png",
    }


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate realistic single-sensor building telemetry with aleth"
    )
    p.add_argument("--scenario", required=True, help="Natural language sensor scenario")
    p.add_argument("--start-year", type=int, default=2025, help="First year to generate")
    p.add_argument("--years", type=int, default=1, help="Number of consecutive years to generate")
    p.add_argument("--freq-minutes", type=int, default=60, help="Measurement interval in minutes")
    p.add_argument("--ollama-url", default=OLLAMA_URL, help="Ollama /api/chat URL")
    p.add_argument("--unit", default=None, help="Optional unit override")
    p.add_argument("--seed", type=int, default=42, help="Random seed")
    p.add_argument("--verbose", action="store_true", help="Print raw JSON responses from the LLM")

    p.add_argument(
        "--results-dir",
        default="results",
        help="Base directory where each run is stored under its own timestamped folder",
    )
    p.add_argument(
        "--run-timestamp",
        default=None,
        help="Optional run timestamp override (default: current local time, format YYYYMMDD_HHMMSS)",
    )

    p.add_argument("--progress", action="store_true", help="Print stage/progress logs to stderr")
    p.add_argument("--show-prompts", action="store_true", help="Show prompt previews in logs")
    p.add_argument("--event-log", default=None, help="Optional JSONL file for structured observability events")
    p.add_argument(
        "--tqdm",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Show tqdm progress bar",
    )

    p.add_argument("--list-stream-examples", action="store_true", help="Print example stream prompts and exit")

    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.list_stream_examples:
        for example in get_stream_examples():
            print(example)
        return 0

    if args.years < 1:
        raise SystemExit("--years must be >= 1")
    if args.freq_minutes < 1 or 1440 % args.freq_minutes != 0:
        raise SystemExit(
            "--freq-minutes must be a positive divisor of 1440, e.g. 1, 5, 10, 15, 30, 60"
        )

    run_timestamp = args.run_timestamp or dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = build_run_paths(args.results_dir, run_timestamp)
    paths["run_dir"].mkdir(parents=True, exist_ok=True)

    event_log_path = None
    if args.event_log:
        event_log_path = str(paths["run_dir"] / args.event_log)
        ensure_parent_dir(Path(event_log_path))

    years = [args.start_year + i for i in range(args.years)]
    unit_hint = args.unit or infer_unit_from_scenario(args.scenario)

    obs = Observability(
        enabled=args.progress or args.show_prompts or bool(event_log_path) or args.tqdm,
        show_prompts=args.show_prompts,
        event_log_path=event_log_path,
        use_tqdm=args.tqdm,
    )
    obs.set_total_steps(estimate_total_hierarchy_steps(years))
    
    obs.info(
        "run_start",
        (
            f"scenario={args.scenario!r}, years={years}, unit_hint={unit_hint}, "
            f"intent_model={MAIN_MODEL_INTENT_PARSING}, "
            f"range_model={MAIN_MODEL_RANGE_ESTIMATOR}, "
            f"run_dir={paths['run_dir']}"
        ),
    )

    intent_client = IntentOllamaClient(
        model=MAIN_MODEL_INTENT_PARSING,
        url=args.ollama_url,
    )

    range_client = OllamaClient(
        model=MAIN_MODEL_RANGE_ESTIMATOR,
        url=args.ollama_url,
    )

    range_estimator = HierarchicalRangeGenerator(
        client=range_client,
        verbose=args.verbose,
        observability=obs,
    )

    orchestrator = SimulationOrchestrator(
        intent_parser=IntentParser(client=intent_client),
        range_estimator=range_estimator,
        spec_generator=SpecGenerator(),
        data_generator=DataGenerator(),
    )

    try:
        result = orchestrator.run(
            scenario=args.scenario,
            years=years,
            unit_hint=unit_hint,
            freq_minutes=args.freq_minutes,
            seed=args.seed,
        )

        rows = result["rows"]
        profile = result["profile"]
        unit = result["unit"]
        hierarchy_json = result["hierarchy_json"]

        csv_path = str(paths["csv"])
        ranges_json_path = str(paths["ranges_json"])
        timeseries_plot_path = str(paths["timeseries_plot"])
        daily_plot_path = str(paths["daily_plot"])
        request_time_plot_path = str(paths["request_time_plot"])
        request_cumulative_plot_path = str(paths["request_cumulative_plot"])

        obs.stage("write_outputs", f"csv={csv_path} json={ranges_json_path}")
        write_csv(rows, csv_path)
        write_json(hierarchy_json, ranges_json_path)

        print_summary(rows, unit)
        print(f"Derived modality profile: {profile.to_dict()}")
        print(f"Run timestamp: {run_timestamp}")
        print(f"Run directory: {paths['run_dir']}")
        print(f"CSV written to: {csv_path}")
        print(f"Ranges JSON written to: {ranges_json_path}")

        obs.stage("plot_timeseries", f"png={timeseries_plot_path}")
        plot_timeseries(
            rows=rows,
            unit=unit,
            scenario=args.scenario,
            output_path=timeseries_plot_path,
        )
        print(f"Timeseries plot written to: {timeseries_plot_path}")

        obs.stage("plot_daily_mean", f"png={daily_plot_path}")
        plot_daily_mean(
            rows=rows,
            unit=unit,
            scenario=args.scenario,
            output_path=daily_plot_path,
        )
        print(f"Daily mean plot written to: {daily_plot_path}")

        obs.stage("plot_request_time", f"png={request_time_plot_path}")
        if plot_request_durations(
            obs=obs,
            scenario=args.scenario,
            output_path=request_time_plot_path,
        ):
            print(f"Request-time plot written to: {request_time_plot_path}")
        else:
            print("Request-time plot skipped: no request duration data available")

        obs.stage(
            "plot_request_cumulative_time",
            f"png={request_cumulative_plot_path}",
        )
        if plot_cumulative_request_time(
            obs=obs,
            scenario=args.scenario,
            output_path=request_cumulative_plot_path,
        ):
            print(f"Cumulative request-time plot written to: {request_cumulative_plot_path}")
        else:
            print("Cumulative request-time plot skipped: no cumulative request timing data available")

        if obs.llm_request_count:
            print(f"LLM requests: {obs.llm_request_count}")
            print(f"Total LLM time: {obs.total_llm_time_s:.3f} s")
            print(f"Average LLM time/request: {obs.total_llm_time_s / obs.llm_request_count:.3f} s")

        obs.summary()
        return 0
    finally:
        obs.close()


if __name__ == "__main__":
    raise SystemExit(main())