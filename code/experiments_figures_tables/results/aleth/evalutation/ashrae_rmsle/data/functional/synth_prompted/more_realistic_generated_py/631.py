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

    # Parameters for realistic pattern
    base = (min_val + max_val) / 2
    amp_daily = (max_val - min_val) / 4
    amp_seasonal = amp_daily / 2
    noise_std = 0.1

    start_dt = datetime(start_year, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(total_hours):
        dt = start_dt + timedelta(hours=i)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday

        daily_component = amp_daily * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_component = amp_seasonal * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, noise_std)

        val = base + daily_component + seasonal_component + noise
        val = max(min_val, min(max_val, val))

        timestamps.append(dt.strftime("%Y-%m-%dT%H:%M"))
        values.append(val)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.plot(dates, values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True, linestyle="--", alpha=0.5)

    # Format x-axis dates
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 631
    min_val = 10.462970339883046
    max_val = 14.974510562437139
    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()