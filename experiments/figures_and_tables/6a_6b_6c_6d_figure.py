import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

COLOR_BGDP2 = "#295e5d"
COLOR_LLM   = "#927686"
MARKER_BGDP2 = "*"
MARKER_LLM   = "^"

BUILDING_IDS = [1135, 113, 272, 1073]

DAYS_LIST = [1, 7, 30]

ROUND = 12
MODEL_SAFE = "gpt-oss_20b"

INTERVAL_HOURS = 1
RESAMPLE_FREQ = "h"

OLLAMA_DIR = "results/off_the_shelf_llms/qualitative/ollama_results_incremental_context"

TRAIN_FEATHER = "../../data/electrical_metering_bgdp2/data_files/train.feather"

OUT_DIR = ""

YEAR = 2016
METER_ID = 0

LINE_RE = re.compile(
    r"(?P<ts>2016-\d{2}-\d{2}\s+\d{2}:\d{2})\s*,\s*(?P<val>-?\d+(?:\.\d+)?)"
)

def expected_measurements(days: int, interval_hours: int = 1) -> int:
    return int(days * 24 / interval_hours)

def count_2016(text: str) -> int:
    return len(re.findall(r"\b2016\b", text))

def llm_file_path(building_id: int, days: int) -> str:
    return os.path.join(
        OLLAMA_DIR,
        f"round_{ROUND}_{MODEL_SAFE}_b{building_id:04d}_{days:03d}_days.txt"
    )

def parse_llm_txt(path: str, days: int) -> pd.DataFrame | None:
    if not os.path.exists(path):
        print(f"Missing LLM file: {path}")
        return None

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    exp = expected_measurements(days, INTERVAL_HOURS)
    c2016 = count_2016(text)

    if c2016 != exp:
        print(f"Invalid sample (count_2016={c2016} != expected={exp}) -> {os.path.basename(path)}")
        return None

    rows = []
    for m in LINE_RE.finditer(text):
        rows.append((m.group("ts"), m.group("val")))

    if len(rows) != exp:
        print(f"Parse mismatch (parsed_rows={len(rows)} != expected={exp}) -> {os.path.basename(path)}")
        return None

    df = pd.DataFrame(rows, columns=["timestamp", "meter_reading"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["meter_reading"] = pd.to_numeric(df["meter_reading"], errors="coerce")
    df = df.dropna(subset=["timestamp", "meter_reading"]).sort_values("timestamp")

    return df.reset_index(drop=True)

def load_train_feather() -> pd.DataFrame:
    train = pd.read_feather(TRAIN_FEATHER)
    train["timestamp"] = pd.to_datetime(train["timestamp"], errors="coerce")
    train = train.dropna(subset=["timestamp", "meter_reading"])
    return train

def actual_window(train: pd.DataFrame, building_id: int, start: pd.Timestamp, end_excl: pd.Timestamp) -> pd.DataFrame:
    df = train.loc[
        (train["building_id"] == building_id) &
        (train["meter"] == METER_ID) &
        (train["timestamp"] >= start) &
        (train["timestamp"] < end_excl),
        ["timestamp", "meter_reading"],
    ].copy()

    if df.empty:
        return df

    df = df.set_index("timestamp").sort_index()

    df = df.resample(RESAMPLE_FREQ).mean()

    df = df.dropna(subset=["meter_reading"]).reset_index()
    return df

def plot_comparison(building_id: int, days: int, actual: pd.DataFrame, llm: pd.DataFrame, out_path: str):
    merged = actual.merge(llm, on="timestamp", how="inner", suffixes=("_actual", "_llm"))

    if merged.empty:
        print(f"No overlapping timestamps for building {building_id}, {days}d")
        return

    plt.figure(figsize=(5, 4))
    plt.plot(
        merged["timestamp"],
        merged["meter_reading_actual"],
        linewidth=2.0,
        alpha=0.9,
        label="Actual (BGDP2)",
        color="#237432",
    )

    plt.plot(
        merged["timestamp"],
        merged["meter_reading_llm"],
        linewidth=1.8,
        alpha=0.85,
        label="LLM (gpt-oss)",
        color="#7f68c3",
    )

    plt.title(f"Real vs LLM data (B. {building_id}); {days}-day interv.")
    plt.xlabel("Timestamp", fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel("Meter Reading (kWh)", fontsize=15)
    plt.legend(frameon=True)
    plt.tight_layout()

    if days == 1:
        ax = plt.gca()
        ax.xaxis.set_major_locator(
            mdates.HourLocator(byhour=[1, 8, 15, 22])
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:00"))
    elif days == 7:
        ax = plt.gca()
        ax.xaxis.set_major_locator(
            mdates.DayLocator(bymonthday=[1, 4, 7])
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/16"))
    elif days == 30:
        ax = plt.gca()
        ax.xaxis.set_major_locator(
            mdates.DayLocator(bymonthday=[2, 15, 29])
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/16"))

    if "1135" in out_path and "1d" in out_path:
        out_path = "figure6a.png"
    elif "113" in out_path and "1d" in out_path:
        out_path = "figure6b.png"
    elif "272" in out_path and "1d" in out_path:
        out_path = "figure6c.png"
    elif "1073" in out_path and "1d" in out_path:
        out_path = "figure6d.png"
    else:
        return 0
    
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")

def main():
    train = load_train_feather()

    start = pd.Timestamp(f"{YEAR}-01-01 00:00:00")

    for bid in BUILDING_IDS:
        for days in DAYS_LIST:
            end_excl = start + pd.Timedelta(days=days)

            llm_path = llm_file_path(bid, days)
            llm_df = parse_llm_txt(llm_path, days)
            if llm_df is None:
                continue

            act_df = actual_window(train, bid, start, end_excl)
            if act_df.empty:
                print(f"No actual data for building {bid}, window {days}d")
                continue

            out_png = os.path.join(OUT_DIR, f"compare_b{bid:04d}_{days:03d}d_actual_vs_llm.png")
            plot_comparison(bid, days, act_df, llm_df, out_png)

if __name__ == "__main__":
    main()