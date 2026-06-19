import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA_DIR = "../../data/electrical_metering_bgdp2/data_files/"
OUT_DIR = "."

FILES = {
    "building_meta_feather": os.path.join(DATA_DIR, "building_metadata.feather"),
    "building_meta_csv": os.path.join(DATA_DIR, "building_metadata.csv"),
    "train_feather": os.path.join(DATA_DIR, "train.feather"),
    "train_csv": os.path.join(DATA_DIR, "train.csv"),
}

METER_ID = 0

YEAR = 2016
DATE_START = f"{YEAR}-01-01"
DATE_END = f"{YEAR}-12-31"
N_PER_TARGET = 15
TARGET_SIZES = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 150000, 200000]
ABS_TOL_SMALL = 200
ABS_TOL_MED = 500
REL_TOL_LARGE = 0.03
AGG_FREQ = "D"
AGG_FUNC = "mean"
RANDOM_SEED = 42

def load_df(feather_path, csv_path, name, usecols=None):
    if os.path.exists(feather_path):
        print(f"Loading {name} from feather")
        try:
            return pd.read_feather(feather_path, columns=usecols)
        except TypeError:
            df = pd.read_feather(feather_path)
            return df[usecols] if usecols else df
    elif os.path.exists(csv_path):
        print(f"Loading {name} from csv")
        return pd.read_csv(csv_path, usecols=usecols)
    else:
        raise FileNotFoundError(f"Could not find {name} file.")


def inclusive_window(start_s, end_s):
    start_ts = pd.to_datetime(start_s)
    end_excl = pd.to_datetime(end_s) + pd.Timedelta(days=1)
    return start_ts, end_excl


def size_bounds(target):
    if target <= 2000:
        return max(1, target - ABS_TOL_SMALL), target + ABS_TOL_SMALL
    if target <= 10000:
        return max(1, target - ABS_TOL_MED), target + ABS_TOL_MED
    return int(target * (1 - REL_TOL_LARGE)), int(target * (1 + REL_TOL_LARGE))


def main():
    np.random.seed(RANDOM_SEED)

    meta = load_df(
        FILES["building_meta_feather"],
        FILES["building_meta_csv"],
        "building_metadata",
        usecols=["building_id", "square_feet"],
    )

    train = load_df(
        FILES["train_feather"],
        FILES["train_csv"],
        "train",
        usecols=["building_id", "meter", "timestamp", "meter_reading"],
    )

    meta["square_feet"] = pd.to_numeric(meta["square_feet"], errors="coerce")
    meta = meta.dropna(subset=["square_feet"])
    meta = meta[meta["square_feet"] > 0].copy()

    train["timestamp"] = pd.to_datetime(train["timestamp"], errors="coerce")
    train = train.dropna(subset=["timestamp", "meter_reading"])

    start_ts, end_excl = inclusive_window(DATE_START, DATE_END)

    train_2016_elec = train.loc[
        (train["meter"] == METER_ID)
        & (train["timestamp"] >= start_ts)
        & (train["timestamp"] < end_excl),
        ["building_id", "timestamp", "meter_reading"],
    ].copy()

    if train_2016_elec.empty:
        raise ValueError("No meter=0 data found in the selected year window.")

    buildings_with_data = set(train_2016_elec["building_id"].unique())
    meta = meta[meta["building_id"].isin(buildings_with_data)].copy()

    print(f"Buildings with meter=0 data in {YEAR}: {meta.shape[0]}")

    selected_rows = []

    selected_ids_all = set()

    for target in TARGET_SIZES:
        low, high = size_bounds(target)
        candidates = meta[(meta["square_feet"] >= low) & (meta["square_feet"] <= high)].copy()

        if candidates.empty:
            print(f"No candidates found for target {target} sqft in range [{low}, {high}]")
            continue

        n_take = min(N_PER_TARGET, candidates.shape[0])
        chosen = candidates.sample(n=n_take, random_state=RANDOM_SEED)

        print(f"Target {target} sqft -> selected {n_take} buildings (range [{low}, {high}])")

        for _, r in chosen.iterrows():
            selected_rows.append({
                "target_sqft": target,
                "range_low": low,
                "range_high": high,
                "building_id": int(r["building_id"]),
                "square_feet": float(r["square_feet"]),
            })
            selected_ids_all.add(int(r["building_id"]))

    sel_df = pd.DataFrame(selected_rows).sort_values(["target_sqft", "square_feet"])

    ts = train_2016_elec[train_2016_elec["building_id"].isin(selected_ids_all)].copy()

    ts = ts.set_index("timestamp")
    if AGG_FUNC == "sum":
        agg = (
            ts.groupby("building_id")["meter_reading"]
            .resample(AGG_FREQ)
            .sum()
            .reset_index()
        )
    else:
        agg = (
            ts.groupby("building_id")["meter_reading"]
            .resample(AGG_FREQ)
            .mean()
            .reset_index()
        )

    for target in TARGET_SIZES:
        target_buildings = sel_df.loc[sel_df["target_sqft"] == target, "building_id"].astype(int).tolist()
        if not target_buildings:
            continue

        plt.figure(figsize=(5, 4))

        for bid in target_buildings:
            b = agg[agg["building_id"] == bid]
            if b.empty:
                continue
            plt.plot(
                b["timestamp"],
                b["meter_reading"],
                linewidth=1.2,
                alpha=0.85,
                label=str(bid),
            )

        low = sel_df.loc[sel_df["target_sqft"] == target, "range_low"].iloc[0]
        high = sel_df.loc[sel_df["target_sqft"] == target, "range_high"].iloc[0]

        plt.title(
            f"{len(target_buildings)} rand. buil. btw. {int(low)/1000:.0f}k-{int(high)/1000:.0f} sqft {AGG_FREQ}-{AGG_FUNC} aggr."
        )
        plt.xlabel("Time", fontsize=13)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        plt.ylabel("Meter reading (kWh)", fontsize=13)
        ax = plt.gca()

        ax.xaxis.set_major_locator(
            mdates.MonthLocator(bymonth=[2, 7, 12])
        )

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

        plt.tight_layout()

        out_png = ""
        if target == 5000:
            out_png = os.path.join(OUT_DIR, f"figure4a.png")
        elif target == 200000:
            out_png = os.path.join(OUT_DIR, f"figure4b.png")
        else:
            out_png = os.path.join(OUT_DIR, f"{target}_sqft.png")
        
        plt.savefig(out_png, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved plot: {out_png}")


if __name__ == "__main__":
    main()
