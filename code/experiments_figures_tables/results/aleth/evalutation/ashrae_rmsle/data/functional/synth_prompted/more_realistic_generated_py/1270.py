#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, start_year, min_val, max_val, seed=42):
    random.seed(seed)
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        hour = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Base consumption
        base = 11.0
        # Daily pattern: higher during day, lower at night
        daily = 2.0 * math.sin(2 * math.pi * hour / 24)
        # Seasonal pattern: slightly higher in winter
        seasonal = 1.0 * math.sin(2 * math.pi * day_of_year / 366)
        # Random noise
        noise = random.gauss(0, 0.2)
        value = base + daily + seasonal + noise
        # Clip to specified range
        value = max(min_val, min(max_val, value))
        timestamps.append(ts)
        values.append(value)
    return timestamps, values

def save_csv(building_id, timestamps, values, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(building_id, timestamps, values, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis dates
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    png_path = os.path.join(output_dir, f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 1270
    start_year = 2016
    min_val = 9.19515035005519
    max_val = 13.591230701261837
    data_dir = "generated_data"
    plot_dir = "generated_plots"

    timestamps, values = generate_data(building_id, start_year, min_val, max_val)
    save_csv(building_id, timestamps, values, data_dir)
    plot_data(building_id, timestamps, values, plot_dir)

if __name__ == "__main__":
    main()