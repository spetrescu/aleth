#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year=2016, building_id=453,
                         min_val=21.771437495978113, max_val=31.535128828917774,
                         seed=42):
    random.seed(seed)
    start = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Base consumption
        base = (min_val + max_val) / 2

        # Daily cycle: higher during day, lower at night
        daily = 3 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle: slight variation over the year
        seasonal = 2 * math.sin(2 * math.pi * day_of_year / 365)

        # Random noise
        noise = random.gauss(0, 0.5)

        value = base + daily + seasonal + noise
        # Clip to specified range
        value = max(min_val, min(max_val, value))

        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 453
    timestamps, values = generate_energy_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f"CSV saved to: {csv_path}")
    print(f"Plot saved to: {png_path}")

if __name__ == "__main__":
    main()