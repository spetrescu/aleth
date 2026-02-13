import os
import re
import numpy as np
import pandas as pd
from datetime import datetime

ROUND = 15
OUTPUT_DIR = "results/off_the_shelf_llms/qualitative/ollama_results_incremental_context"
DATA_DIR = "../../data/electrical_metering_bgdp2/data_files/"
TRAIN_FEATHER = os.path.join(DATA_DIR, "train.feather")
TRAIN_CSV = os.path.join(DATA_DIR, "train.csv")

YEAR = 2016
METER_ID = 0
START_DATE = datetime(2016, 1, 1, 0, 0)
INTERVAL_HOURS = 1
HOURLY_FREQ = "h"
EPS = 1e-9

MODEL_TOKEN = "gpt-oss_20b"

TARGET_BUILDINGS = [1135, 113, 272]
DAYS_TO_EVAL = list(range(1, 32))
REPORT_HORIZONS = [1, 7, 30]

CONTEXT = {
    1135: dict(yearly_mean=263.43817, yearly_min=125.06, yearly_max=479.897, winter_mean=250.41924),
    113:  dict(yearly_mean=363.97446, yearly_min=159.643, yearly_max=679.25,  winter_mean=361.4717),
    272:  dict(yearly_mean=17.38018,  yearly_min=0.8,    yearly_max=74.32,   winter_mean=11.742976),
}

def expected_measurements(days: int) -> int:
    return days * 24


def synth_path(building_id: int, days: int) -> str:
    return os.path.join(
        OUTPUT_DIR,
        f"round_{ROUND}_{MODEL_TOKEN}_b{building_id:04d}_{days:03d}_days.txt"
    )


def load_train() -> pd.DataFrame:
    if os.path.exists(TRAIN_FEATHER):
        print("Loading real train from feather:", os.path.abspath(TRAIN_FEATHER))
        df = pd.read_feather(TRAIN_FEATHER, columns=["building_id", "meter", "timestamp", "meter_reading"])
    elif os.path.exists(TRAIN_CSV):
        print("Loading real train from csv:", os.path.abspath(TRAIN_CSV))
        df = pd.read_csv(TRAIN_CSV, usecols=["building_id", "meter", "timestamp", "meter_reading"])

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["meter_reading"] = pd.to_numeric(df["meter_reading"], errors="coerce")
    df = df.dropna(subset=["timestamp", "meter_reading"])
    df = df[(df["meter"] == METER_ID) & (df["timestamp"].dt.year == YEAR)].copy()
    return df


def real_slice_stats(train_df: pd.DataFrame, building_id: int, days: int) -> dict:
    start = pd.Timestamp(START_DATE)
    end = start + pd.Timedelta(days=days)

    b = train_df[train_df["building_id"] == building_id].copy()
    if b.empty:
        return {"real_mean": np.nan, "real_std": np.nan, "real_n": 0}

    b = b[(b["timestamp"] >= start) & (b["timestamp"] < end)].copy()
    if b.empty:
        return {"real_mean": np.nan, "real_std": np.nan, "real_n": 0}

    hourly = b.set_index("timestamp")["meter_reading"].resample(HOURLY_FREQ).mean().dropna()
    if hourly.empty:
        return {"real_mean": np.nan, "real_std": np.nan, "real_n": 0}

    return {
        "real_mean": float(hourly.mean()),
        "real_std": float(hourly.std(ddof=0)),
        "real_n": int(hourly.shape[0]),
    }


def parse_synth_file(path: str) -> dict:
    ts_list, val_list = [], []

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            s = raw.strip()
            if not s:
                continue
            if "," not in s:
                return {"ok": False}
            left, right = s.split(",", 1)

            ts = pd.to_datetime(left.strip(), errors="coerce")
            if pd.isna(ts):
                return {"ok": False}

            try:
                val = float(right.strip())
            except Exception:
                return {"ok": False}

            ts_list.append(ts)
            val_list.append(val)

    if not ts_list:
        return {"ok": False}

    return {"ok": True, "ts": pd.DatetimeIndex(ts_list), "values": np.array(val_list, dtype=float)}


def is_exact_hourly_grid(ts: pd.DatetimeIndex, days: int) -> bool:
    exp_n = expected_measurements(days)
    if len(ts) != exp_n:
        return False
    if ts[0] != pd.Timestamp(START_DATE):
        return False
    diffs = ts[1:] - ts[:-1]
    return (diffs == pd.Timedelta(hours=INTERVAL_HOURS)).all()

def evaluate_one(train_df: pd.DataFrame, building_id: int, days: int) -> dict:
    ctx = CONTEXT[building_id]
    exp_n = expected_measurements(days)

    path = synth_path(building_id, days)

    if not os.path.exists(path):
        return {
            "building_id": building_id,
            "days": days,
            "found": False,
            "valid": False,
            "in_bounds_pct": 0.0,
            "mean_err_vs_yearly": np.nan,
            "mean_err_vs_winter": np.nan,
            "mean_err_vs_real": np.nan,
            "std_err_vs_real": np.nan,
            "mean_z_err": np.nan,
            "real_cov_pct": np.nan,
        }

    parsed = parse_synth_file(path)
    if not parsed.get("ok"):
        return {
            "building_id": building_id,
            "days": days,
            "found": True,
            "valid": False,
            "in_bounds_pct": 0.0,
            "mean_err_vs_yearly": np.nan,
            "mean_err_vs_winter": np.nan,
            "mean_err_vs_real": np.nan,
            "std_err_vs_real": np.nan,
            "mean_z_err": np.nan,
            "real_cov_pct": np.nan,
        }

    ts = parsed["ts"]
    vals = parsed["values"]

    valid = (len(vals) == exp_n) and is_exact_hourly_grid(ts, days)

    if not valid:
        return {
            "building_id": building_id,
            "days": days,
            "found": True,
            "valid": False,
            "in_bounds_pct": 0.0,
            "mean_err_vs_yearly": np.nan,
            "mean_err_vs_winter": np.nan,
            "mean_err_vs_real": np.nan,
            "std_err_vs_real": np.nan,
            "mean_z_err": np.nan,
            "real_cov_pct": np.nan,
        }

    lo, hi = float(ctx["yearly_min"]), float(ctx["yearly_max"])
    inb = np.logical_and(vals >= lo, vals <= hi)
    in_bounds_pct = 100.0 * float(np.mean(inb))

    synth_mean = float(np.mean(vals))

    mean_err_vs_yearly = abs(synth_mean - float(ctx["yearly_mean"]))
    mean_err_vs_winter = abs(synth_mean - float(ctx["winter_mean"]))

    rs = real_slice_stats(train_df, building_id, days)
    real_cov_pct = 100.0 * (rs["real_n"] / exp_n) if exp_n > 0 else np.nan

    mean_err_vs_real = np.nan
    std_err_vs_real = np.nan
    mean_z_err = np.nan

    if np.isfinite(rs["real_mean"]):
        mean_err_vs_real = abs(synth_mean - float(rs["real_mean"]))

    if np.isfinite(rs["real_std"]):
        synth_std = float(np.std(vals, ddof=0))
        std_err_vs_real = abs(synth_std - float(rs["real_std"]))
        if np.isfinite(mean_err_vs_real):
            mean_z_err = mean_err_vs_real / (float(rs["real_std"]) + EPS)

    return {
        "building_id": building_id,
        "days": days,
        "found": True,
        "valid": True,
        "in_bounds_pct": in_bounds_pct,
        "mean_err_vs_yearly": mean_err_vs_yearly,
        "mean_err_vs_winter": mean_err_vs_winter,
        "mean_err_vs_real": mean_err_vs_real,
        "std_err_vs_real": std_err_vs_real,
        "mean_z_err": mean_z_err,
        "real_cov_pct": real_cov_pct,
    }


def horizon_score(rows_h: pd.DataFrame) -> float:
    n = len(rows_h)
    if n == 0:
        return np.nan

    valid_frac = float(rows_h["valid"].mean())
    mean_inb = float(rows_h["in_bounds_pct"].mean()) / 100.0

    zvals = rows_h.loc[rows_h["valid"] & rows_h["mean_z_err"].notna(), "mean_z_err"].values
    mean_z = float(np.mean(zvals)) if len(zvals) else np.nan

    if not np.isfinite(mean_z):
        mean_z = 0.0

    score = 100.0 * valid_frac * mean_inb * float(np.exp(-mean_z))
    return score


def summarize_horizon(df: pd.DataFrame, days: int) -> dict:
    d = df[df["days"] == days].copy()
    n = len(d)
    if n == 0:
        return {"days": days, "n": 0}

    valid_pct = 100.0 * float(d["valid"].mean())
    in_bounds_pct = float(d["in_bounds_pct"].mean())
    score = horizon_score(d)

    valid_only = d[d["valid"]].copy()

    def mean_valid(col):
        x = valid_only[col].dropna().values
        return float(np.mean(x)) if len(x) else np.nan

    return {
        "days": days,
        "n": n,
        "valid_pct": valid_pct,
        "in_bounds_pct": in_bounds_pct,
        "mean_err_vs_yearly": mean_valid("mean_err_vs_yearly"),
        "mean_err_vs_winter": mean_valid("mean_err_vs_winter"),
        "mean_err_vs_real": mean_valid("mean_err_vs_real"),
        "std_err_vs_real": mean_valid("std_err_vs_real"),
        "mean_z_err": mean_valid("mean_z_err"),
        "real_cov_pct": mean_valid("real_cov_pct"),
        "score": score,
        "found": int(d["found"].sum()),
        "invalid": int((~d["valid"]).sum()),
    }


def print_summary_block(title: str, summaries: list[dict]):
    print(title)

    print("\nContext-based proxy checks (invalid INCLUDED in Valid% and In-bounds%):")
    header = f"{'Horizon':>8} | {'n':>3} | {'Found':>5} | {'Invalid':>7} | {'Valid%':>7} | {'In-b%':>7} | {'M.err yearly':>11} | {'M.err winter':>11} | {'Score':>8}"
    print(header)
    print("-" * len(header))
    for s in summaries:
        d = s["days"]
        lab = "1 day" if d == 1 else f"{d} days"
        print(
            f"{lab:>8} | {s['n']:>3} | {s['found']:>5} | {s['invalid']:>7} | "
            f"{s['valid_pct']:>7.2f} | {s['in_bounds_pct']:>7.2f} | "
            f"{(s['mean_err_vs_yearly'] if np.isfinite(s['mean_err_vs_yearly']) else np.nan):>11.3f} | "
            f"{(s['mean_err_vs_winter'] if np.isfinite(s['mean_err_vs_winter']) else np.nan):>11.3f} | "
            f"{(s['score'] if np.isfinite(s['score']) else np.nan):>8.2f}"
        )

    print("\nReal-slice proxy checks (errors over valid only; validity penalized in Score above):")
    header2 = f"{'Horizon':>8} | {'Valid%':>7} | {'RealCov%':>8} | {'M.err mean':>10} | {'Std err':>9} | {'Mean z-err':>10}"
    print(header2)
    print("-" * len(header2))
    for s in summaries:
        d = s["days"]
        lab = "1 day" if d == 1 else f"{d} days"
        print(
            f"{lab:>8} | {s['valid_pct']:>7.2f} | "
            f"{(s['real_cov_pct'] if np.isfinite(s['real_cov_pct']) else np.nan):>8.2f} | "
            f"{(s['mean_err_vs_real'] if np.isfinite(s['mean_err_vs_real']) else np.nan):>10.3f} | "
            f"{(s['std_err_vs_real'] if np.isfinite(s['std_err_vs_real']) else np.nan):>9.3f} | "
            f"{(s['mean_z_err'] if np.isfinite(s['mean_z_err']) else np.nan):>10.3f}"
        )


def main():
    print(f"Evaluating ROUND {ROUND} | model token={MODEL_TOKEN} | dir={OUTPUT_DIR}")
    print(f"Buildings={TARGET_BUILDINGS} | days=1..31 | report horizons={REPORT_HORIZONS}")

    train_df = load_train()

    rows = []
    for bid in TARGET_BUILDINGS:
        for days in DAYS_TO_EVAL:
            rows.append(evaluate_one(train_df, bid, days))

    df = pd.DataFrame(rows)

    summaries = [summarize_horizon(df, d) for d in REPORT_HORIZONS]
    print_summary_block("Proxy realism summary by horizon (GPT-OSS only, invalids included)", summaries)

    overall = df.copy()
    overall_valid_pct = 100.0 * float(overall["valid"].mean())
    overall_inb = float(overall["in_bounds_pct"].mean())
    overall_score = horizon_score(overall.assign(days=0))
    total_expected = len(TARGET_BUILDINGS) * len(DAYS_TO_EVAL)
    total_found = int(overall["found"].sum())
    total_invalid = int((~overall["valid"]).sum())

    print("Overall (all horizons 1..31) — invalids included")
    print(f"Expected files: {total_expected} | Found: {total_found} | Invalid: {total_invalid}")
    print(f"Valid% (incl. missing/invalid): {overall_valid_pct:.2f}%")
    print(f"In-bounds% (invalids contribute 0): {overall_inb:.2f}%")
    print(f"Final proxy score (penalizes invalid + mean mismatch): {overall_score:.2f}")


if __name__ == "__main__":
    main()