import csv
import json
import os
import re
import sys
from pathlib import Path

import requests


OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b")

TAGS_URL = f"{OLLAMA_HOST}/api/tags"
GENERATE_URL = f"{OLLAMA_HOST}/api/generate"

BASE_DIR = Path(__file__).resolve().parent
BUILDINGS_CSV = BASE_DIR / "builds.csv"
GENERATED_PY_DIR = BASE_DIR / "generated_py"

CODE_BEGIN = "<CODE BEGIN>"
CODE_END = "<CODE END>"


def build_prompt(building_id: str, min_value: float, max_value: float) -> str:
    return f"""You are generating Python code only.

Write a complete Python 3 script for this task:

Energy metering for a sensor between {min_value} and {max_value} kWh.
Generate such data over the period of 1 year, with the start date in 2016.
The measurements must be hourly.

Requirements:
- Save the data as a CSV.
- The first column must be named "timestamp".
- The second column must be named "value".
- Timestamp format must look like: 2016-01-01T00:00
- Use matplotlib to visualize the data points.
- Save the figure as a PNG.
- The building id is: {building_id}
- Save the CSV to: generated_data/{building_id}.csv
- Save the PNG to: generated_plots/{building_id}.png
- Create output directories if needed.
- The script must be self-contained and runnable directly.
- Use only standard Python libraries plus matplotlib.
- The generated data should look realistic for hourly energy metering over a year.
- Make the output deterministic by setting a random seed.
- Include an if __name__ == "__main__": entry point.

Very important:
- Return ONLY Python code.
- Put {CODE_BEGIN} on its own line before the code.
- Put {CODE_END} on its own line after the code.
- Do not include any explanation.
"""


def check_ollama_server() -> None:
    try:
        r = requests.get(TAGS_URL, timeout=15)
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {OLLAMA_HOST}. Original error: {exc}"
        ) from exc

    if r.status_code != 200:
        raise RuntimeError(
            f"Ollama health check failed. GET {TAGS_URL} returned "
            f"status {r.status_code} with body: {r.text[:500]}"
        )

    try:
        data = r.json()
    except Exception as exc:
        raise RuntimeError(
            f"GET {TAGS_URL} did not return JSON. Response was: {r.text[:500]}"
        ) from exc

    models = [m.get("name", "") for m in data.get("models", [])]
    if not models:
        print("[WARN] Ollama is reachable, but no models were listed.")
    else:
        print(f"[INFO] Ollama reachable. Models: {', '.join(models)}")

    if OLLAMA_MODEL not in models:
        print(
            f"[WARN] Requested model '{OLLAMA_MODEL}' was not found. "
            f"Available models: {models}"
        )


def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 4096
        }
    }

    response = requests.post(GENERATE_URL, json=payload, timeout=600)

    if response.status_code != 200:
        raise RuntimeError(
            f"POST {GENERATE_URL} failed with status {response.status_code}. "
            f"Response body: {response.text[:1000]}"
        )

    try:
        data = response.json()
    except Exception as exc:
        raise RuntimeError(
            f"POST {GENERATE_URL} did not return valid JSON. "
            f"Response body: {response.text[:1000]}"
        ) from exc

    if "response" not in data:
        raise RuntimeError(f"Unexpected Ollama response: {json.dumps(data, indent=2)}")

    return data["response"]


def extract_code(text: str) -> str:
    text = text.strip()

    # Best case: both tokens exist
    full_pattern = re.compile(
        rf"{re.escape(CODE_BEGIN)}\s*(.*?)\s*{re.escape(CODE_END)}",
        re.DOTALL,
    )
    match = full_pattern.search(text)
    if match:
        return match.group(1).strip()

    # Fallback: only CODE_BEGIN exists
    begin_index = text.find(CODE_BEGIN)
    if begin_index != -1:
        code = text[begin_index + len(CODE_BEGIN):].strip()
        if code:
            print("[WARN] Missing <CODE END>; saving partial code anyway.")
            return code

    # Fallback: extract fenced python block
    fence_pattern = re.compile(r"```python\s*(.*?)```", re.DOTALL | re.IGNORECASE)
    match = fence_pattern.search(text)
    if match:
        print("[WARN] Missing code tokens; extracted from fenced code block.")
        return match.group(1).strip()

    # Final fallback: save raw output if it looks like python
    if "def " in text or "import " in text or "if __name__ ==" in text:
        print("No tokens found; saving raw model output as code.")
        return text

    raise ValueError(
        "Could not extract Python code from model output.\n"
        f"Model output was:\n{text[:2000]}"
    )


def save_code(building_id: str, code: str) -> Path:
    GENERATED_PY_DIR.mkdir(parents=True, exist_ok=True)
    output_path = GENERATED_PY_DIR / f"{building_id}.py"
    output_path.write_text(code, encoding="utf-8")
    return output_path


def validate_input_file() -> None:
    if not BUILDINGS_CSV.exists():
        raise FileNotFoundError(
            f"Could not find {BUILDINGS_CSV}. Make sure builds.csv is next to this script."
        )


def main() -> int:
    validate_input_file()
    check_ollama_server()

    generated = 0
    failed = 0

    with BUILDINGS_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        required_columns = {"building_id", "min_meter_reading", "max_meter_reading"}
        if not required_columns.issubset(reader.fieldnames or set()):
            raise ValueError(
                f"CSV must contain columns: {sorted(required_columns)}. "
                f"Found: {reader.fieldnames}"
            )

        for row in reader:
            building_id = row["building_id"].strip()
            min_value = float(row["min_meter_reading"])
            max_value = float(row["max_meter_reading"])

            print(f"[INFO] Generating code for building {building_id}...")

            try:
                prompt = build_prompt(building_id, min_value, max_value)
                raw_response = call_ollama(prompt)
                code = extract_code(raw_response)
                saved_path = save_code(building_id, code)
                print(f"[OK] Saved: {saved_path}")
                generated += 1
            except Exception as exc:
                print(f"[ERROR] Building {building_id} failed: {exc}", file=sys.stderr)
                failed += 1

    print(f"\nDone. Generated={generated}, Failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())