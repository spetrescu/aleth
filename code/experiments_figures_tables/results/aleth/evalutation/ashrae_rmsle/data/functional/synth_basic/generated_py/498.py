#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, start_year, min_val, max_val, seed=42):
    random.seed(seed)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        timestamps.append(ts)
        # Daily sinusoidal pattern
        hour_of_day = ts.hour
        base = 27.5 + 5 * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.gauss(0, 0.5)
        val = base + noise
        # Clamp to given range
        val = max(min_val, min(max_val, val))
        values.append(val)
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
    plt.title(f"Hourly Energy Metering for Sensor {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    png_path = os.path.join(output_dir, f"{building_id}.png")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    building_id = 498
    start_year = 2016
    min_val = 22.41569420643628
    max_val = 32.54442686179401
    csv_dir = "generated_data"
    plot_dir = "generated_plots"

    timestamps, values = generate_data(building_id, start_year, min_val, max_val)
    save_csv(building_id, timestamps, values, csv_dir)
    plot_data(building_id, timestamps, values, plot_dir)

if __name__ == "__main__":
    main()