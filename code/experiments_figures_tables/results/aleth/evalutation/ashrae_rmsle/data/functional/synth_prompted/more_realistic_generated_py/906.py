#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int):
    random.seed(42)

    # Define output directories
    csv_dir = os.path.join("generated_data")
    png_dir = os.path.join("generated_plots")
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(png_dir, exist_ok=True)

    csv_path = os.path.join(csv_dir, f"{building_id}.csv")
    png_path = os.path.join(png_dir, f"{building_id}.png")

    # Time range: entire year
    start_dt = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    end_dt = datetime(start_year, 12, 31, 23, 0)

    # Parameters for realistic pattern
    base = 53.7  # midpoint of the given range
    amp_daily = 5.0
    amp_weekly = 2.0
    amp_seasonal = 3.0
    noise_std = 0.5
    min_val = 43.629498481995476
    max_val = 63.74054239460782

    timestamps = []
    values = []

    current = start_dt
    while current <= end_dt:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday

        # Daily cycle
        daily = amp_daily * math.sin(2 * math.pi * hour_of_day / 24)

        # Weekly cycle
        weekly = amp_weekly * math.sin(2 * math.pi * day_of_year / 7)

        # Seasonal cycle
        seasonal = amp_seasonal * math.sin(2 * math.pi * day_of_year / 365)

        # Random noise
        noise = random.gauss(0, noise_std)

        value = base + daily + weekly + seasonal + noise
        # Clip to specified range
        value = max(min_val, min(max_val, value))

        timestamps.append(current.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

        current += timedelta(hours=1)

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    # Convert timestamps to matplotlib date format
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    ax.plot(dates, values, linewidth=0.5)
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Energy (kWh)")
    ax.set_title(f"Hourly Energy Metering for Building {building_id} (2016)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close(fig)

if __name__ == "__main__":
    generate_energy_data(start_year=2016, building_id=906)