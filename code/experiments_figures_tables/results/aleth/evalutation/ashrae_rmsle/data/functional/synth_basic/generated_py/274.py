#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt

def generate_energy_data(building_id: int,
                         start_year: int = 2016,
                         min_val: float = 25.70392138761401,
                         max_val: float = 37.15381577759296):
    # Ensure deterministic output
    random.seed(0)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # File paths
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    png_path = os.path.join(plot_dir, f"{building_id}.png")

    # Time range: 2016 is a leap year (366 days)
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    total_hours = 366 * 24  # 8784 hours

    timestamps = []
    values = []

    base = (min_val + max_val) / 2.0  # midpoint

    for hour_offset in range(total_hours):
        ts = start_dt + datetime.timedelta(hours=hour_offset)
        timestamps.append(ts)

        # Daily variation: higher during day, lower at night
        daily_variation = 3.0 * math.sin(2 * math.pi * ts.hour / 24)

        # Seasonal variation: higher in winter, lower in summer
        day_of_year = ts.timetuple().tm_yday
        seasonal_variation = 2.0 * math.sin(2 * math.pi * (day_of_year - 1) / 366)

        # Random noise
        noise = random.uniform(-0.5, 0.5)

        value = base + daily_variation + seasonal_variation + noise
        # Clip to allowed range
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val

        values.append(value)

    # Write CSV
    with open(csv_path, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Energy consumption for building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

if __name__ == "__main__":
    generate_energy_data(building_id=274)
</CODE END>