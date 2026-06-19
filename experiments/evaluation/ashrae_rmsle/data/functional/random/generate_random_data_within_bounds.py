import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

if len(sys.argv) < 2:
    print("Usage: python generate_meter_readings.py <input_file.csv> [seed]")
    print("Example: python generate_meter_readings.py buildings_ranges.csv 42")
    sys.exit(1)

input_file = sys.argv[1]
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42

np.random.seed(seed)
print(f"Random seed set to: {seed}")

os.makedirs("data", exist_ok=True)
os.makedirs("plots", exist_ok=True)

print(f"Reading building ranges from {input_file}...")
ranges_df = pd.read_csv(input_file)

required_cols = {"building_id", "min_meter_reading", "max_meter_reading"}
if not required_cols.issubset(ranges_df.columns):
    print(f"Error: Input file must contain columns: {required_cols}")
    sys.exit(1)

print("Generating 8784 hourly timestamps for 2016...")
dates = pd.date_range(
    start="2016-01-01 00:00:00",
    periods=366 * 24,
    freq="h"
)

timestamp_str = dates.strftime("%Y-%m-%dT%H:%M")

print(f"Processing {len(ranges_df)} buildings with seed {seed}...\n")

for idx, row in ranges_df.iterrows():
    building_id = int(row["building_id"])
    min_val = float(row["min_meter_reading"])
    max_val = float(row["max_meter_reading"])

    print(f"  → Building {building_id} | Range: {min_val:.2f} – {max_val:.2f}")

    values = np.random.uniform(low=min_val, high=max_val, size=len(dates))

    df = pd.DataFrame({
        "timestamp": timestamp_str,
        "value": values
    })

    csv_path = f"{building_id}_random.csv"
    df.to_csv(csv_path, index=False)

    plt.figure(figsize=(14, 6))
    plt.plot(dates, values, linewidth=0.8, alpha=0.7, color='#1f77b4')
    plt.title(f"Hourly Meter Readings - Building {building_id}\n"
              f"Range: {min_val:.2f} – {max_val:.2f} (Seed: {seed})")
    plt.xlabel("Date (2016)")
    plt.ylabel("Meter Reading Value")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plot_path = f"plots/building_{building_id}.png"
    plt.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close()

print("\nGeneration completed successfully!")
print(f"Random seed used : {seed}")
print(f"CSV files saved in : ./")
print(f"Plots saved in      : ./plots/")
print(f"Buildings processed : {len(ranges_df)}")
print(f"Hours per building  : {len(dates):,} (full year 2016)")
