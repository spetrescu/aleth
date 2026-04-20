#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # File paths
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    png_path = os.path.join(plot_dir, f"{building_id}.png")

    # Time range: 1 year hourly
    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year, 12, 31, 23, 0)
    total_hours = int(((end_dt - start_dt).total_seconds() // 3600) + 1)

    timestamps = []
    values = []

    base = 40.0  # base consumption
    daily_amp = 5.0
    weekly_amp = 3.0
    seasonal_amp = 4.0
    noise_std = 0.5

    for i in range(total_hours):
        dt = start_dt + timedelta(hours=i)
        hour = dt.hour
        day_of_week = dt.weekday()  # Monday=0
        day_of_year = dt.timetuple().tm_yday

        # Sine waves for daily, weekly, seasonal patterns
        daily = daily_amp * math.sin(2 * math.pi * hour / 24)
        weekly = weekly_amp * math.sin(2 * math.pi * day_of_week / 7)
        seasonal = seasonal_amp * math.sin(2 * math.pi * day_of_year / 365)

        noise = random.gauss(0, noise_std)

        value = base + daily + weekly + seasonal + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(dt)
        values.append(value)

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Energy Metering Data for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    generate_energy_data(
        start_year=2016,
        building_id=388,
        min_val=35.46100515374695,
        max_val=51.38038026469263
    )
</CODE END>