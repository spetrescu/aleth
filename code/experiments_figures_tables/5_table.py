import os
import re
import numpy as np
import pandas as pd

TRAIN_FEATHER = "../../data/electrical_metering_bgdp2/data_files/train.feather"
METER_ID = 0

BUILDING_ID = 113
YEAR = 2016
START_TS = pd.Timestamp(f"{YEAR}-01-01 00:00:00")
FREQ = "h"
RESAMPLE_FREQ = "h"

Y_MIN = 159.643
Y_MAX = 679.25

DAYS_AVAILABLE = [1, 7]

NORMAL_DIR = "results/off_the_shelf_llms/qualitative/ollama_results_incremental_context"

NORMAL_ROUND = 15
NORMAL_MODEL_SAFE = "gpt-oss_20b"

ANOM_DIR = "results/off_the_shelf_llms/qualitative/ollama_results_anomalies_b113_round16"
ANOM_ROUND = 16
ANOM_MODEL_SAFE = "gpt-oss_20b"

ANOMALY_TYPES = ["A_OOB_ALL", "B_INB_SPIKES"]

_LINE_RE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*,\s*([+-]?\d+(?:\.\d+)?)\s*$")

def make_index(start: pd.Timestamp, days: int) -> pd.DatetimeIndex:
    return pd.date_range(start, periods=days * 24, freq=FREQ)

def parse_ollama_timeseries(path: str) -> pd.Series:
    if not os.path.exists(path):
        return pd.Series(dtype=float)

    ts = []
    vals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = _LINE_RE.match(line)
            if not m:
                continue
            t = pd.to_datetime(m.group(1), errors="coerce")
            if pd.isna(t):
                continue
            ts.append(t)
            vals.append(float(m.group(2)))

    if not ts:
        return pd.Series(dtype=float)

    s = pd.Series(vals, index=pd.DatetimeIndex(ts), name=os.path.basename(path)).sort_index()
    return s

def load_real_hourly(train_feather: str, building_id: int, start: pd.Timestamp, end_excl: pd.Timestamp) -> pd.Series:
    df = pd.read_feather(train_feather)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "meter_reading"])

    d = df.loc[
        (df["building_id"] == building_id)
        & (df["meter"] == METER_ID)
        & (df["timestamp"] >= start)
        & (df["timestamp"] < end_excl),
        ["timestamp", "meter_reading"],
    ].copy()

    if d.empty:
        return pd.Series(dtype=float)

    d = d.set_index("timestamp").sort_index()
    s = d["meter_reading"].resample(RESAMPLE_FREQ).mean().dropna()
    s.name = "BGDP2"
    return s

def normal_file_path(building_id: int, days: int) -> str:
    fn = f"round_{NORMAL_ROUND}_{NORMAL_MODEL_SAFE}_b{building_id:04d}_{days:03d}_days.txt"
    return os.path.join(NORMAL_DIR, fn)

def anomaly_file_path(building_id: int, days: int, anomaly_type: str) -> str:
    fn = f"round_{ANOM_ROUND}_{ANOM_MODEL_SAFE}_b{building_id:04d}_{days:03d}_days_{anomaly_type}.txt"
    return os.path.join(ANOM_DIR, fn)

def compute_metrics(s: pd.Series, y_min: float, y_max: float) -> dict:
    s = s.dropna()
    n = int(s.shape[0])
    if n == 0:
        return {"n": 0, "mean": np.nan, "std": np.nan, "oob_pct": np.nan, "max_ex": np.nan}

    vals = s.values.astype(float)

    below = vals < y_min
    above = vals > y_max
    oob = below | above
    oob_pct = 100.0 * float(oob.sum()) / float(n)

    ex = np.zeros_like(vals, dtype=float)
    ex[below] = (y_min - vals[below])
    ex[above] = (vals[above] - y_max)
    max_ex = float(np.max(ex)) if ex.size else np.nan

    return {
        "n": n,
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals, ddof=1)) if n >= 2 else 0.0,
        "oob_pct": oob_pct,
        "max_ex": max_ex,
    }

def fmt(x: float, nd=3) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "--"
    return f"{x:.{nd}f}"

def main():
    for days in DAYS_AVAILABLE:
        end_excl = START_TS + pd.Timedelta(days=days)
        idx = make_index(START_TS, days)

        real = load_real_hourly(TRAIN_FEATHER, BUILDING_ID, START_TS, end_excl).reindex(idx)
        baseline = parse_ollama_timeseries(normal_file_path(BUILDING_ID, days)).reindex(idx)

        oob = parse_ollama_timeseries(anomaly_file_path(BUILDING_ID, days, "A_OOB_ALL")).reindex(idx)
        spikes = parse_ollama_timeseries(anomaly_file_path(BUILDING_ID, days, "B_INB_SPIKES")).reindex(idx)

        series_map = {
            "BGDP2": real,
            "Synth. (baseline)": baseline,
            "Synth. (OOB)": oob,
            "Synth. (spikes)": spikes,
        }

        rows = []
        for name, s in series_map.items():
            m = compute_metrics(s, Y_MIN, Y_MAX)
            rows.append({
                "Trace": name,
                "n": m["n"],
                "Mean (kWh)": m["mean"],
                "Std (kWh)": m["std"],
                "OOB%": m["oob_pct"],
                "Max ex. (kWh)": m["max_ex"],
            })

        out_df = pd.DataFrame(rows)

        print(f"\nBuilding {BUILDING_ID}: #{days} day(s)")
        print(f"Bounds: [{Y_MIN}, {Y_MAX}]")
        print(out_df.to_string(index=False, formatters={
            "Mean (kWh)": lambda x: fmt(x, 3),
            "Std (kWh)": lambda x: fmt(x, 3),
            "OOB%": lambda x: fmt(x, 2),
            "Max ex. (kWh)": lambda x: fmt(x, 3),
        }))

if __name__ == "__main__":
    main()
