import os
import re
import csv
import time
import random
from datetime import datetime
from typing import Optional, Tuple

import requests

BASE = "http://localhost:11434"
MODELS = ["gpt-oss:20b"]

TIMEOUT = 360
MAX_ATTEMPTS_PER_REQUEST = 3

BUILDING_ID = 113
INTERVAL_TIME_IN_HOURS = 1
START_DATE = datetime(2016, 1, 1)

DAYS_TO_TEST = [1, 7, 30]
DAYS_TO_TEST = [1, 7]
ANOMALY_TYPES = ["A_OOB_ALL", "B_INB_SPIKES"]
ANOMALY_TYPES = ["B_INB_SPIKES"]

OUTPUT_DIR = "ollama_results_anomalies_b113_round16"
os.makedirs(OUTPUT_DIR, exist_ok=True)

ROUND = 16

BUILDINGS = [
    {"building_id": 1135, "primary_use": "Education", "square_feet": 150393,
     "yearly_mean_kwh": 263.43817, "yearly_min_kwh": 125.06, "yearly_max_kwh": 479.897,
     "summer_mean_kwh": 263.8639, "winter_mean_kwh": 250.41924, "stability_score": 1.8547977112652363},
    {"building_id": 113, "primary_use": "Education", "square_feet": 100481,
     "yearly_mean_kwh": 363.97446, "yearly_min_kwh": 159.643, "yearly_max_kwh": 679.25,
     "summer_mean_kwh": 365.49576, "winter_mean_kwh": 361.4717, "stability_score": 1.571778617186692},
    {"building_id": 272, "primary_use": "Education", "square_feet": 4583,
     "yearly_mean_kwh": 17.38018, "yearly_min_kwh": 0.8, "yearly_max_kwh": 74.32,
     "summer_mean_kwh": 25.539513, "winter_mean_kwh": 11.742976, "stability_score": 1.4613530307707578},
    {"building_id": 1073, "primary_use": "Office", "square_feet": 194111,
     "yearly_mean_kwh": 179.21414, "yearly_min_kwh": 0.0, "yearly_max_kwh": 853.0,
     "summer_mean_kwh": 118.158516, "winter_mean_kwh": 230.26053, "stability_score": 1.4515084282987074},
]

def _get_building_row(building_id: int) -> dict:
    for b in BUILDINGS:
        if int(b["building_id"]) == int(building_id):
            return b
    raise ValueError(f"Building {building_id} not found in BUILDINGS list.")

def build_prompt_anomaly(
    building_row: dict,
    start_date: datetime,
    interval_hours: int,
    num_measurements: int,
    anomaly_type: str,
) -> str:
    """
    Two anomaly types:
      A_OOB_ALL     : entire trace out-of-bounds (systematically above max or below min)
      B_INB_SPIKES  : mostly within bounds, but with occasional spikes that exceed bounds
    """
    date_str = start_date.strftime("%d %B %Y")

    common_header = f"""
You are generating electricity meter readings (kWh) for ONE building.

Building metadata and annual summary statistics (2016):
- building_id: {building_row['building_id']}
- primary_use: {building_row['primary_use']}
- square_feet: {building_row['square_feet']}
- yearly_mean_kwh: {building_row['yearly_mean_kwh']}
- yearly_min_kwh: {building_row['yearly_min_kwh']}
- yearly_max_kwh: {building_row['yearly_max_kwh']}
- summer_mean_kwh (Jun-Aug): {building_row['summer_mean_kwh']}
- winter_mean_kwh (Dec-Feb): {building_row['winter_mean_kwh']}

Generate data at {interval_hours}-hour intervals starting on {date_str}
for exactly {num_measurements} measurements.

Output format constraints:
- Output ONLY lines of: "YYYY-MM-DD HH:MM,VALUE"
- Exactly {num_measurements} lines (no headers, no extra text).
- Do NOT truncate output.
""".strip()

    if anomaly_type == "A_OOB_ALL":
        anomaly_instructions = f"""
Anomaly scenario A (systematically out-of-bounds, every point):
- This is a faulty sensor or calibration failure.
- EVERY single value must be OUTSIDE the permissible range [{building_row['yearly_min_kwh']}, {building_row['yearly_max_kwh']}].
- Keep the series realistic-looking (daily periodicity + small noise), but it must be consistently out-of-bounds.
- Prefer being above yearly_max_kwh most of the time (e.g., 5% to 30% above max), but it can occasionally drop below min.
""".strip()

    elif anomaly_type == "B_INB_SPIKES":
        anomaly_instructions = f"""
Anomaly scenario B (mostly in-bounds with spikes):
- Normal operation MOST of the time: keep the majority of values within [{building_row['yearly_min_kwh']}, {building_row['yearly_max_kwh']}], centered near yearly_mean_kwh with daily periodicity + small noise.
- Inject sporadic spikes: around 1 spike per day on average.
- Spikes must be clearly anomalous and exceed the bounds (above yearly_max_kwh or below yearly_min_kwh).
- Apart from spikes, avoid touching the bounds too often.
""".strip()

    else:
        raise ValueError(f"Unknown anomaly_type: {anomaly_type}")

    tail = """
Return the full dataset now.
""".strip()

    return "\n\n".join([common_header, anomaly_instructions, tail]).strip()

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

def ollama_native_generate(model: str, prompt: str) -> str:
    url = f"{BASE}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": False}
    r = requests.post(url, json=payload, timeout=TIMEOUT, allow_redirects=False)
    if r.status_code != 200:
        raise RuntimeError(_debug_response(r))
    return r.json().get("response", "")

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
    return r.json()["choices"][0]["message"]["content"]

def call_ollama(model: str, prompt: str, max_attempts: int = MAX_ATTEMPTS_PER_REQUEST) -> Tuple[str, str, float]:
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        t0 = time.perf_counter()
        try:
            text = ollama_native_generate(model, prompt)
            return text, "native:/api/generate", (time.perf_counter() - t0)
        except Exception as e_native:
            try:
                text = ollama_openai_chat(model, prompt)
                return text, "openai:/v1/chat/completions", (time.perf_counter() - t0)
            except Exception as e_v1:
                last_exc = (e_native, e_v1)

        if attempt < max_attempts:
            sleep_s = min(30.0, (2 ** (attempt - 1)) + random.random())
            print(f"call_ollama failed (attempt {attempt}/{max_attempts}) model={model}; retrying in {sleep_s:.1f}s")
            time.sleep(sleep_s)

    e_native, e_v1 = last_exc
    print("Native endpoint failed:\n", e_native)
    print("\nFallback endpoint failed:\n", e_v1)
    raise RuntimeError(f"Both endpoints failed after {max_attempts} attempts for model={model}")

def count_measurements_by_2016(text: str) -> int:
    return len(re.findall(r"\b2016\b", text))

def save_output(model: str, building_id: int, days: int, anomaly_type: str, content: str) -> str:
    safe_model = model.replace(":", "_")
    filename = f"round_{ROUND}_{safe_model}_b{building_id:04d}_{days:03d}_days_{anomaly_type}.txt"
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {path}  ({len(content)} chars)")
    return path

def summary_csv_path() -> str:
    return os.path.join(OUTPUT_DIR, f"round_{ROUND}_summary_results.csv")

def append_result_csv(row: dict, path: str):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "building_id",
                "requested_days",
                "anomaly_type",
                "expected_measurements",
                "actual_measurements",
                "response_time_s",
                "endpoint_used",
                "chars",
                "output_path",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def generate_one(model: str, building_row: dict, days: int, anomaly_type: str) -> dict:
    expected_measurements = days * 24
    prompt = build_prompt_anomaly(
        building_row=building_row,
        start_date=START_DATE,
        interval_hours=INTERVAL_TIME_IN_HOURS,
        num_measurements=expected_measurements,
        anomaly_type=anomaly_type,
    )

    print(f"Model {model} | b{building_row['building_id']} | {days} days | {anomaly_type}")
    t0 = time.perf_counter()
    text, endpoint_used, _elapsed = call_ollama(model, prompt)
    elapsed_s = time.perf_counter() - t0

    actual_measurements = count_measurements_by_2016(text)
    out_path = save_output(model, int(building_row["building_id"]), days, anomaly_type, text)

    row = {
        "model": model,
        "building_id": int(building_row["building_id"]),
        "requested_days": int(days),
        "anomaly_type": anomaly_type,
        "expected_measurements": int(expected_measurements),
        "actual_measurements": int(actual_measurements),
        "response_time_s": round(float(elapsed_s), 6),
        "endpoint_used": endpoint_used,
        "chars": int(len(text)),
        "output_path": out_path,
    }
    return row

if __name__ == "__main__":
    b = _get_building_row(BUILDING_ID)
    csv_path = summary_csv_path()

    results = []
    for model in MODELS:
        for anomaly_type in ANOMALY_TYPES:
            for days in DAYS_TO_TEST:
                row = generate_one(model, b, days, anomaly_type)
                results.append(row)
                append_result_csv(row, csv_path)

    print(os.path.abspath(OUTPUT_DIR))
