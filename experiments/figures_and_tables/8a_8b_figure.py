import os
import re
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

YEAR = 2016
START_TS = pd.Timestamp(f"{YEAR}-01-01 00:00:00")
FREQ = "h"
RESAMPLE_FREQ = "h"
METER_ID = 0

TRAIN_FEATHER = "../../data/electrical_metering_bgdp2/data_files/train.feather"

BUILDING = {
    "building_id": 113,
    "primary_use": "Education",
    "square_feet": 100481,
    "yearly_mean_kwh": 363.97446,
    "yearly_min_kwh": 159.643,
    "yearly_max_kwh": 679.25,
    "summer_mean_kwh": 365.49576,
    "winter_mean_kwh": 361.4717,
    "stability_score": 1.571778617186692,
}

HORIZONS_DAYS = [1, 7]

NORMAL_DIR = "results/off_the_shelf_llms/qualitative/ollama_results_incremental_context"
NORMAL_ROUND = 15
NORMAL_MODEL_SAFE = "gpt-oss_20b"

ANOM_DIR = "results/off_the_shelf_llms/qualitative/ollama_results_anomalies_b113_round16"
ANOM_ROUND = 16
ANOM_MODEL_SAFE = "gpt-oss_20b"

ANOMALY_TYPES = ["A_OOB_ALL", "B_INB_SPIKES"]

OUT_DIR = "."
os.makedirs(OUT_DIR, exist_ok=True)

COLOR_REAL = "#176C21"
COLOR_NORMAL = "#5A34D6"
COLOR_ANOM = "#D934A8"
COLOR_BOUNDS = "#E45756"

def load_train() -> pd.DataFrame:
    df = pd.read_feather(TRAIN_FEATHER)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "meter_reading"])
    return df

def real_hourly_window(train: pd.DataFrame, building_id: int, start: pd.Timestamp, end_excl: pd.Timestamp) -> pd.Series:
    d = train.loc[
        (train["building_id"] == building_id)
        & (train["meter"] == METER_ID)
        & (train["timestamp"] >= start)
        & (train["timestamp"] < end_excl),
        ["timestamp", "meter_reading"],
    ].copy()

    if d.empty:
        return pd.Series(dtype=float)

    d = d.set_index("timestamp").sort_index()
    d = d.resample(RESAMPLE_FREQ).mean().dropna()
    return d["meter_reading"]

_LINE_RE = re.compile(r"^\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*,\s*([+-]?\d+(?:\.\d+)?)\s*$")

def parse_ollama_timeseries(path: str) -> pd.Series:
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    ts = []
    vals = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = _LINE_RE.match(line)
            if not m:
                continue
            t = pd.to_datetime(m.group(1), errors="coerce")
            v = float(m.group(2))
            if pd.isna(t):
                continue
            ts.append(t)
            vals.append(v)

    if not ts:
        return pd.Series(dtype=float)

    s = pd.Series(vals, index=pd.DatetimeIndex(ts), name=os.path.basename(path))
    s = s.sort_index()
    return s

def make_time_index(days: int) -> pd.DatetimeIndex:
    return pd.date_range(START_TS, periods=days * 24, freq=FREQ)

def normal_file_path(building_id: int, days: int) -> str:
    fn = f"round_{NORMAL_ROUND}_{NORMAL_MODEL_SAFE}_b{building_id:04d}_{days:03d}_days.txt"
    return os.path.join(NORMAL_DIR, fn)

def anomaly_file_path(building_id: int, days: int, anomaly_type: str) -> str:
    fn = f"round_{ANOM_ROUND}_{ANOM_MODEL_SAFE}_b{building_id:04d}_{days:03d}_days_{anomaly_type}.txt"
    return os.path.join(ANOM_DIR, fn)

def plot_three_horizons_normal_vs_anom_vs_real(
    train: pd.DataFrame,
    building: dict,
    anomaly_type: str,
    out_path: str,
):
    y_min = float(building["yearly_min_kwh"])
    y_max = float(building["yearly_max_kwh"])

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(5, 5), sharey=False)

    for ax, days in zip(axes, HORIZONS_DAYS):
        idx = make_time_index(days)
        end_excl = START_TS + pd.Timedelta(days=days)

        real = real_hourly_window(train, int(building["building_id"]), START_TS, end_excl)

        n_path = normal_file_path(int(building["building_id"]), days)
        normal = parse_ollama_timeseries(n_path)

        a_path = anomaly_file_path(int(building["building_id"]), days, anomaly_type)
        anom = parse_ollama_timeseries(a_path)

        df_plot = pd.DataFrame(index=idx)
        if not real.empty:
            df_plot["real"] = real.reindex(idx)
        if not normal.empty:
            df_plot["normal"] = normal.reindex(idx)
        if not anom.empty:
            df_plot["anomaly"] = anom.reindex(idx)

        if "real" in df_plot.columns and df_plot["real"].notna().any():
            ax.plot(
                df_plot.index, df_plot["real"].values,
                linewidth=2.0, alpha=0.9, color=COLOR_REAL,
                label="Real (BGDP2)" if days == 1 else None,
                marker=">"
            )

        if "normal" in df_plot.columns and df_plot["normal"].notna().any():
            ax.plot(
                df_plot.index, df_plot["normal"].values,
                linewidth=1.8, alpha=0.85, color=COLOR_NORMAL,
                label="gpt-oss (normal)" if days == 1 else None,
                marker="*"
            )

        if "anomaly" in df_plot.columns and df_plot["anomaly"].notna().any():
            ax.plot(
                df_plot.index, df_plot["anomaly"].values,
                linewidth=1.8, alpha=0.85, color=COLOR_ANOM,
                label=f"gpt-oss (anomaly: {"OOB" if anomaly_type == "A_OOB_ALL" else "Spikes"})" if days == 1 else None,
                marker="^",
            )

        ax.axhline(
            y=y_min, linewidth=1.6, alpha=0.95, linestyle="--", color=COLOR_BOUNDS,
            label="Permissible bounds (min/max)" if days == 1 else None,
        )
        ax.axhline(y=y_max, linewidth=1.6, alpha=0.95, linestyle="--", color=COLOR_BOUNDS)

        ax.set_title(f"{days}-day interval - Real vs. norm. vs. anomalous OOB (B. {building['building_id']})", fontsize=11)
        ax.set_xlabel("Time")
        ax.set_ylabel("kWh")
        ax.grid(True, axis="y", alpha=0.3)
        if days == 1:
            ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif days == 7:
            ax = plt.gca()
            ax.xaxis.set_major_locator(
                mdates.DayLocator(bymonthday=[1, 4, 7])
            )
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/16"))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", frameon=True)

    plt.tight_layout(rect=[0, 0, 1, 0.92])
    if "OOB" in out_path:
        out_path = "figure8a.png"
    if "SPIKES" in out_path:
        out_path = "figure8b.png"
    plt.savefig(out_path, dpi=150)
    plt.close()

def main():
    train = load_train()

    for anomaly_type in ANOMALY_TYPES:
        out_path = os.path.join(
            OUT_DIR,
            f"b{int(BUILDING['building_id']):04d}_normal_vs_{anomaly_type}_vs_real.png",
        )
        plot_three_horizons_normal_vs_anom_vs_real(
            train=train,
            building=BUILDING,
            anomaly_type=anomaly_type,
            out_path=out_path,
        )

if __name__ == "__main__":
    main()
