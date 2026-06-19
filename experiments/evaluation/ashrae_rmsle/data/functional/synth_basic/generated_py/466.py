#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start = datetime(start_year, 1, 1, 0, 0)
    total_hours = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Base consumption
        base = 36.0

        # Daily variation: higher during day, lower at night
        daily_variation = 4.0 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal variation: slight change over the year
        seasonal_variation = 2.0 * math.sin(2 * math.pi * (day_of_year - 1) / 365)

        # Random noise
        noise = random.uniform(-0.5, 0.5)

        value = base + daily_variation + seasonal_variation + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title("Hourly Energy Metering")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 466
    min_val = 31.23050016015093
    max_val = 44.932407093144626

    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)

    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()