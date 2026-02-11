import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import acf

DATA_DIR = "../../data/electrical_metering_bgdp2/data_files/"

FILES = {
    "building_meta_feather": os.path.join(DATA_DIR, "building_metadata.feather"),
    "building_meta_csv": os.path.join(DATA_DIR, "building_metadata.csv"),
    "train_feather": os.path.join(DATA_DIR, "train.feather"),
    "train_csv": os.path.join(DATA_DIR, "train.csv"),
}

PRIMARY_USES = ["Office", "Education", "Lodging/residential"]
METER_ID = 0
AGG_FREQ = "h"
MIN_POINTS = 24 * 14

def load_df(feather_path, csv_path, name, usecols=None):
    if os.path.exists(feather_path):
        try:
            return pd.read_feather(feather_path, columns=usecols)
        except TypeError:
            df = pd.read_feather(feather_path)
            return df[usecols] if usecols else df
    elif os.path.exists(csv_path):
        return pd.read_csv(csv_path, usecols=usecols)
    else:
        raise FileNotFoundError(f"Could not find {name} file.")

def main():
    building_meta = load_df(
        FILES["building_meta_feather"],
        FILES["building_meta_csv"],
        "building_metadata",
        usecols=["building_id", "primary_use"],
    )

    train = load_df(
        FILES["train_feather"],
        FILES["train_csv"],
        "train",
        usecols=["building_id", "meter", "timestamp", "meter_reading"],
    )

    train["timestamp"] = pd.to_datetime(train["timestamp"], errors="coerce")
    train = train.dropna(subset=["timestamp", "meter_reading"])

    results = []

    for pu in PRIMARY_USES:
        ids = set(building_meta.loc[building_meta["primary_use"] == pu, "building_id"])
        base = train.loc[
            (train["building_id"].isin(ids)) & (train["meter"] == METER_ID),
            ["building_id", "timestamp", "meter_reading"],
        ].copy()

        if base.empty:
            continue

        for bid, g in base.groupby("building_id"):
            ts = g.set_index("timestamp")["meter_reading"].resample(AGG_FREQ).mean()
            ts = ts.dropna()

            if len(ts) < MIN_POINTS:
                continue

            y = ts.values

            try:
                acfs = acf(y, nlags=168, fft=True)
                acf_24 = acfs[24] if len(acfs) > 24 else np.nan
                acf_168 = acfs[168] if len(acfs) > 168 else np.nan
                cyclicality_score = np.nanmean([abs(acf_24), abs(acf_168)])
            except Exception:
                cyclicality_score = np.nan

            if len(y) > 168:
                y_true = y[168:]
                y_pred = y[:-168]
                mae = np.mean(np.abs(y_true - y_pred))
            else:
                mae = np.nan

            cv = np.std(y) / np.mean(y) if np.mean(y) != 0 else np.nan
            roughness = np.mean(np.abs(np.diff(y)))

            results.append({
                "building_id": bid,
                "primary_use": pu,
                "cyclicality_score": cyclicality_score,
                "seasonal_mae": mae,
                "cv": cv,
                "roughness": roughness,
            })

    df = pd.DataFrame(results)

    summary = (
        df.groupby("primary_use")
        .agg(
            n_buildings=("building_id", "count"),
            mean_cyclicality=("cyclicality_score", "mean"),
            mean_seasonal_mae=("seasonal_mae", "mean"),
            mean_cv=("cv", "mean"),
            mean_roughness=("roughness", "mean"),
        )
        .reset_index()
    )

    print("\nSummary by building type:\n")
    print(summary.to_string(index=False))

    plt.figure(figsize=(5, 4))
    data = [df.loc[df["primary_use"] == pu, "cyclicality_score"].dropna() for pu in PRIMARY_USES]
    plt.boxplot(data, labels=PRIMARY_USES, showfliers=False, medianprops=dict(color="turquoise", linewidth=2))
    plt.title("Cyclicality score by building type (ACF @ 24 & 168)")
    plt.ylabel("Cyclicality score",fontsize=11)
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.savefig("figure3a.png", dpi=150)
    plt.close()

if __name__ == "__main__":
    main()
