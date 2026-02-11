import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap, BoundaryNorm

DATA_DIR = Path(".")

TRAIN_FEATHER = DATA_DIR / "../../data/electrical_metering_bgdp2/data_files/train.feather"
TRAIN_CSV     = DATA_DIR / "../../data/electrical_metering_bgdp2/data_files/train.csv"

METER_LABELS = {
    0: "Electricity",
    1: "Chilled Water",
    2: "Steam",
    3: "Hot Water",
}

if TRAIN_FEATHER.exists():
    train = pd.read_feather(TRAIN_FEATHER)
elif TRAIN_CSV.exists():
    train = pd.read_csv(TRAIN_CSV)

required = {"timestamp", "building_id", "meter", "meter_reading"}
missing = required - set(train.columns)
if missing:
    raise ValueError(f"train is missing columns: {missing}. Found columns: {list(train.columns)}")

train["timestamp"] = pd.to_datetime(train["timestamp"])
train = train.set_index("timestamp").sort_index()

COLOR_ZERO = "#757575"
COLOR_NONZERO = "#009964"

cmap = ListedColormap([COLOR_ZERO, COLOR_NONZERO])
norm = BoundaryNorm([-0.5, 0.5, 1.5], cmap.N)

sns.set_theme(style="white")
fig, axes = plt.subplots(1, 4, figsize=(8, 3), constrained_layout=True)

n_buildings = int(train["building_id"].max()) + 1

for meter in range(4):
    df = train[train["meter"] == meter].reset_index()

    t0 = df["timestamp"].min()
    df["hour"] = ((df["timestamp"] - t0) / pd.Timedelta(hours=1)).astype("int64")

    max_hour = int(df["hour"].max())
    missmap = np.full((n_buildings, max_hour + 1), np.nan, dtype=float)

    vals = (df["meter_reading"].to_numpy() != 0).astype(float)
    rows = df["building_id"].to_numpy(dtype=int)
    cols = df["hour"].to_numpy(dtype=int)
    missmap[rows, cols] = vals

    ax = axes[meter]
    ax.set_title(METER_LABELS[meter], fontsize=10)
    ax.set_xlabel("Hour since first timestamp")
    ax.set_ylabel("Building ID")

    sns.heatmap(
        missmap,
        cmap=cmap,
        norm=norm,
        ax=ax,
        cbar=False,
        mask=np.isnan(missmap),
        linewidths=0,
        rasterized=True,
    )

out_path = "figure1.png"
fig.savefig(out_path, bbox_inches="tight", dpi=200)
plt.close(fig)

print(f"Saved: {out_path}")


METER_LABELS = {
    0: "Electricity",
    1: "Chilled Water",
    2: "Steam",
    3: "Hot Water",
}

measurement_counts = (
    train
    .groupby("meter")
    .size()
    .rename("n_measurements")
    .reset_index()
)

measurement_counts["meter_label"] = measurement_counts["meter"].map(METER_LABELS)

print(measurement_counts)