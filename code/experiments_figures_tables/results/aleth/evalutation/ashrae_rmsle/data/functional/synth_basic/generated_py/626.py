#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_data():
    random.seed(42)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Parameters
    building_id = 626
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    png_path = os.path.join(plot_dir, f"{building_id}.png")

    # Time range: 2016-01-01 00:00 to 2016-12-31 23:00 (leap year)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 8784 hours

    timestamps = []
    raw_values = []

    for hour_index in range(total_hours):
        current_time = start + datetime.timedelta(hours=hour_index)
        timestamps.append(current_time)

        hour_of_day = current_time.hour
        day_of_year = current_time.timetuple().tm_yday

        # Base consumption
        base = 0.3  # kWh

        # Daily variation
        daily_variation = 0.1 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal variation
        seasonal_variation = 0.05 * math.sin(2 * math.pi * day_of_year / 366)

        # Random noise
        noise = random.uniform(-0.02, 0.02)

        value = base + daily_variation + seasonal_variation + noise
        value = max(value, 0.0)  # Ensure non-negative
        raw_values.append(value)

    # Scale to target total energy
    sum_raw = sum(raw_values)
    target_total = random.uniform(99.29119702755428, 146.60474599327966)
    scale_factor = target_total / sum_raw
    scaled_values = [v * scale_factor for v in raw_values]

    # Write CSV
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, scaled_values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, scaled_values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

if __name__ == "__main__":
    generate_data()
</CODE END>