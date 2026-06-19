#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, start_year, min_val, max_val, seed=42):
    random.seed(seed)
    total_hours = 366 * 24  # 2016 is a leap year
    start = datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []

    amplitude = (max_val - min_val) / 2.0
    offset = (max_val + min_val) / 2.0

    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        base = offset + amplitude * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.uniform(-0.05, 0.05)
        val = base + noise
        val = max(min_val, min(max_val, val))
        timestamps.append(ts)
        values.append(val)

    return timestamps, values

def save_csv(building_id, timestamps, values, directory):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{building_id}.csv")
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(building_id, timestamps, values, directory):
    os.makedirs(directory, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    filepath = os.path.join(directory, f"{building_id}.png")
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 186
    start_year = 2016
    min_val = 1.1917655751288687
    max_val = 1.853626057189711
    csv_dir = "generated_data"
    plot_dir = "generated_plots"

    timestamps, values = generate_data(building_id, start_year, min_val, max_val)
    save_csv(building_id, timestamps, values, csv_dir)
    plot_data(building_id, timestamps, values, plot_dir)

if __name__ == "__main__":
    main()