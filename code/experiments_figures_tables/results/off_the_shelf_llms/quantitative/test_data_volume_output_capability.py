import requests
from datetime import datetime
import os
import re
import csv
import time
import sys
import random
from typing import Optional

import matplotlib.pyplot as plt

BASE = "http://localhost:11434"
MODELS = ["llama3.2", "llama3.1:8b", "gpt-oss:20b"]  # "deepseek-r1",

OUTPUT_DIR = "qualitative_results_incremental_by_no_days"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TIMEOUT = 360
ROUND = 11

MAX_ATTEMPTS_PER_REQUEST = 3

MAX_CONSECUTIVE_FAILURES_PER_MODEL = 3

RESUME_FROM_EXISTING_CSV = True

PALETTE = [
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#E45756",
    "#B279A2",
    "#72B7B2",
    "#9D755D",
    "#BAB0AC",
]
HATCHES = ["///", "\\\\", "xx", "..", "++", "--", "oo", "**"]


def _debug_response(r: requests.Response) -> str:
    body = r.text
    if len(body) > 1500:
        body = body[:1500] + "\n...<truncated>..."
    return (
        f"Request URL: {r.request.method} {r.request.url}\n"
        f"Status: {r.status_code}\n"
        f"Headers: {dict(r.headers)}\n"
        f"Body:\n{body}\n"
    )


def build_prompt(
    building_size_sqft: int,
    start_date: datetime,
    interval_hours: int,
    num_measurements: int,
) -> str:
    date_str = start_date.strftime("%d %B %Y")
    prompt = f"""
I want you to generate me building sensor data, specifically electrical metering for a building that is {building_size_sqft} sq feet.
Simply return measurements, with date and electrical measurement in kWh, on each line separated by a comma.
Generate such data starting on {date_str}, at {interval_hours}-hour intervals.
Give me the entire span of the data, namely {num_measurements} data measurements.
Don't truncate the output.
"""
    return prompt.strip()

def build_prompt(
    building_size_sqft: int,
    start_date: datetime,
    interval_hours: int,
    num_measurements: int,
) -> str:
    date_str = start_date.strftime("%d %B %Y")
    prompt = f"""
I want you to generate me building sensor data, specifically electrical metering for a building that is {building_size_sqft} sq feet.
Simply return measurements, with date and electrical measurement in kWh, on each line separated by a comma.
Generate such data starting on {date_str}, at {interval_hours}-hour intervals.
Give me the entire span of the data, namely {num_measurements} data measurements.
Don't truncate the output -- return the data at all costs, regardless of limits.
"""
    return prompt.strip()

def ollama_native_generate(model: str, prompt: str) -> str:
    url = f"{BASE}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    r = requests.post(url, json=payload, timeout=TIMEOUT, allow_redirects=False)
    if r.status_code != 200:
        raise RuntimeError(_debug_response(r))
    data = r.json()
    return data.get("response", "")


def ollama_openai_chat(model: str, prompt: str) -> str:
    url = f"{BASE}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "stream": False,
    }
    r = requests.post(url, json=payload, timeout=TIMEOUT, allow_redirects=False)
    if r.status_code != 200:
        raise RuntimeError(_debug_response(r))
    data = r.json()
    return data["choices"][0]["message"]["content"]


def call_ollama(model: str, prompt: str, max_attempts: int = MAX_ATTEMPTS_PER_REQUEST) -> tuple[str, str, float]:
    last_exc = None

    for attempt in range(1, max_attempts + 1):
        t0 = time.perf_counter()

        try:
            text = ollama_native_generate(model, prompt)
            used = "native:/api/generate"
            elapsed = time.perf_counter() - t0
            return text, used, elapsed

        except Exception as e_native:
            try:
                text = ollama_openai_chat(model, prompt)
                used = "openai:/v1/chat/completions"
                elapsed = time.perf_counter() - t0
                return text, used, elapsed

            except Exception as e_v1:
                last_exc = (e_native, e_v1)

        if attempt < max_attempts:
            sleep_s = min(30.0, (2 ** (attempt - 1)) + random.random())
            print(f"call_ollama failed (attempt {attempt}/{max_attempts}) for model={model}; retrying in {sleep_s:.1f}s")
            time.sleep(sleep_s)

    e_native, e_v1 = last_exc
    print("Native endpoint failed:\n", e_native)
    print("\nFallback endpoint failed:\n", e_v1)
    raise RuntimeError(f"Both endpoints failed after {max_attempts} attempts for model={model}")


def eject_model(model: str) -> bool:
    url = f"{BASE}/api/generate"
    payload = {
        "model": model,
        "prompt": "",
        "stream": False,
        "keep_alive": 0,
    }
    try:
        r = requests.post(url, json=payload, timeout=TIMEOUT, allow_redirects=False)
        ok = (r.status_code == 200)
        if not ok:
            print(f"eject_model({model}) got status {r.status_code}")
        return ok
    except Exception as e:
        print(f"eject_model({model}) failed: {e}")
        return False

def count_measurements_by_2016(text: str) -> int:
    return len(re.findall(r"2016", text))

def save_output(model: str, days: int, content: str):
    safe_model = model.replace(":", "_")
    filename = f"round_{ROUND}_{safe_model}_{days:03d}_days.txt"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {path}  ({len(content)} chars)")


def _summary_csv_path() -> str:
    return os.path.join(OUTPUT_DIR, f"round_{ROUND}_summary_results.csv")

def _measurements_plot_path() -> str:
    return os.path.join(OUTPUT_DIR, f"round_{ROUND}_measurements.png")

def _timing_plot_path() -> str:
    return os.path.join(OUTPUT_DIR, f"round_{ROUND}_response_times.png")

# This is to load existing rows if present, to support resume (as sometimes ollama serve dies due to errors)
def _read_existing_results(csv_path: str) -> list[dict]:
    if not os.path.exists(csv_path):
        return []
    rows: list[dict] = []
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "model": r["model"],
                "requested_days": int(r["requested_days"]),
                "expected_measurements": int(r["expected_measurements"]),
                "actual_measurements": int(r["actual_measurements"]),
                "response_time_s": float(r["response_time_s"]),
                "endpoint_used": r["endpoint_used"],
                "chars": int(r["chars"]),
            })
    return rows


def write_results_csv(results: list, path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "requested_days",
                "expected_measurements",
                "actual_measurements",
                "response_time_s",
                "endpoint_used",
                "chars",
            ],
        )
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f"Saved CSV summary to: {path}")


def append_result_csv(row: dict, path: str):
    """
    Append a single row to CSV, creating file with header if needed.
    This makes the run robust to crashes: you keep progress.
    """
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "requested_days",
                "expected_measurements",
                "actual_measurements",
                "response_time_s",
                "endpoint_used",
                "chars",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def generate_for_days(
    model: str,
    building_size_sqft: int,
    start_date: datetime,
    interval_hours: int,
    days: int,
) -> dict:
    expected_measurements = days * 24

    prompt = build_prompt(
        building_size_sqft,
        start_date,
        interval_hours,
        expected_measurements,
    )

    print(f"  {model}: requesting {days} day(s)...")
    text, endpoint_used, elapsed_s = call_ollama(model, prompt)

    actual_measurements = count_measurements_by_2016(text)
    char_len = len(text)

    print(f"    requested_days        = {days}")
    print(f"    expected_measurements = {expected_measurements}")
    print(f"    actual_measurements   = {actual_measurements}")
    print(f"    response_time_s       = {elapsed_s:.3f}")
    print(f"    endpoint_used         = {endpoint_used}")
    print(f"    chars_written         = {char_len}")

    save_output(model, days, text)

    return {
        "model": model,
        "requested_days": days,
        "expected_measurements": expected_measurements,
        "actual_measurements": actual_measurements,
        "response_time_s": round(elapsed_s, 6),
        "endpoint_used": endpoint_used,
        "chars": char_len,
    }

def _model_style(models: list[str]) -> dict:
    styles = {}
    for i, m in enumerate(models):
        styles[m] = (PALETTE[i % len(PALETTE)], HATCHES[i % len(HATCHES)])
    return styles


def plot_measurements(results: list, path: str):
    if not results:
        print("No results to plot (measurements).")
        return

    models = sorted({r["model"] for r in results})
    days_sorted = sorted({r["requested_days"] for r in results})
    lookup = {(r["model"], r["requested_days"]): r for r in results}
    styles = _model_style(models)

    plt.figure(figsize=(12, 6))
    bar_width = 0.8 / max(1, len(models))
    x = list(range(len(days_sorted)))

    for i, model in enumerate(models):
        color, hatch = styles[model]
        x_shifted = [xi + i * bar_width for xi in x]

        for xi, d in zip(x_shifted, days_sorted):
            row = lookup.get((model, d))
            if row is None:
                continue

            y_act = row["actual_measurements"]

            plt.bar(
                xi,
                y_act,
                width=bar_width,
                label=model if d == days_sorted[0] else None,  # label once
                alpha=0.9,
                color=color,
                edgecolor="black",
                linewidth=0.8,
                hatch=hatch,
            )

            expected = d * 24
            marker_color = "green" if y_act >= expected else "red"
            plt.hlines(
                y=expected,
                xmin=xi - bar_width * 0.42,
                xmax=xi + bar_width * 0.42,
                colors=marker_color,
                linewidth=3,
            )

    center_positions = [xi + bar_width * (len(models) - 1) / 2 for xi in x]
    plt.xticks(center_positions, days_sorted)

    plt.xlabel("Requested days")
    plt.ylabel("Number of measurements")
    plt.title("Actual Measurements vs. expected (days × 24)")
    plt.legend(title="Model")
    plt.grid(True, axis="y", linewidth=0.6, alpha=0.6)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved plot to: {path}")


def plot_response_times(results: list, path: str):
    if not results:
        print("No results to plot (response times).")
        return

    models = sorted({r["model"] for r in results})
    days_sorted = sorted({r["requested_days"] for r in results})
    lookup = {(r["model"], r["requested_days"]): r for r in results}
    styles = _model_style(models)

    plt.figure(figsize=(12, 6))
    bar_width = 0.8 / max(1, len(models))
    x = list(range(len(days_sorted)))

    for i, model in enumerate(models):
        color, hatch = styles[model]
        x_shifted = [xi + i * bar_width for xi in x]

        for xi, d in zip(x_shifted, days_sorted):
            row = lookup.get((model, d))
            if row is None:
                continue

            y_time = row["response_time_s"]

            plt.bar(
                xi,
                y_time,
                width=bar_width,
                label=model if d == days_sorted[0] else None,  # label once
                alpha=0.9,
                color=color,
                edgecolor="black",
                linewidth=0.8,
                hatch=hatch,
            )

    center_positions = [xi + bar_width * (len(models) - 1) / 2 for xi in x]
    plt.xticks(center_positions, days_sorted)

    plt.xlabel("Requested days")
    plt.ylabel("Response time (seconds)")
    plt.title("Response Time vs. eequested Days")
    plt.legend(title="Model")
    plt.grid(True, axis="y", linewidth=0.6, alpha=0.6)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved plot to: {path}")


def finalize_artifacts(results: list):
    csv_path = _summary_csv_path()
    measurements_plot_path = _measurements_plot_path()
    timing_plot_path = _timing_plot_path()

    results_sorted = sorted(results, key=lambda r: (r["model"], r["requested_days"]))

    write_results_csv(results_sorted, csv_path)
    plot_measurements(results_sorted, measurements_plot_path)
    plot_response_times(results_sorted, timing_plot_path)

if __name__ == "__main__":
    building_size = 10_000
    interval_hours = 1
    start_date = datetime(2016, 1, 1)

    csv_path = _summary_csv_path()

    results: list[dict] = []
    completed = set()

    if RESUME_FROM_EXISTING_CSV and os.path.exists(csv_path):
        existing = _read_existing_results(csv_path)
        results.extend(existing)
        completed = {(r["model"], r["requested_days"]) for r in existing}
        print(f"Resuming: loaded {len(existing)} rows from {csv_path}")

    try:
        for model in MODELS:
            print(f"=== Starting model: {model} ===")

            consecutive_failures = 0

            for days in range(61, 62):  # change to range(1, 366) for full run
                if (model, days) in completed:
                    print(f"\n=== Skipping {model} / {days} day(s) (already in CSV) ===")
                    continue

                print(f"\n=== Generating for {days} day(s) ===")
                try:
                    row = generate_for_days(
                        model=model,
                        building_size_sqft=building_size,
                        start_date=start_date,
                        interval_hours=interval_hours,
                        days=days,
                    )
                    results.append(row)
                    completed.add((model, days))

                    append_result_csv(row, csv_path)

                    consecutive_failures = 0

                except Exception as e:
                    consecutive_failures += 1
                    print(f"Failed for model={model}, days={days}: {e}")

                    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES_PER_MODEL:
                        print(f"Stopping model early due to {consecutive_failures} consecutive failures: {model}")
                        break

            print(f"\n--- Ejecting model: {model} ---")
            ok = eject_model(model)
            print(f"    eject_model status: {'ok' if ok else 'failed/warn'}")

    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C). Will write plots for partial results.")
    except Exception as e:
        print(f"\nUnhandled exception: {e}. Will write plots for partial results.")
    finally:
        finalize_artifacts(results)
        print("Done.")
