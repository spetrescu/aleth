#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        day_of_year = ts.timetuple().tm_yday  # 1-366
        hour_of_day = ts.hour
        seasonal = 0.5 + 0.5 * math.sin(2 * math.pi * (day_of_year - 1) / 366)
        daily = 0.5 + 0.5 * math.sin(2 * math.pi * hour_of_day / 24)
        base = min_val + (max_val - min_val) * seasonal * daily
        noise = random.gauss(0, 0.5)
        value = max(min_val, min(max_val, base + noise))
        timestamps.append(ts)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id: int):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, linestyle='-', marker=None)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 141
    min_kwh = 48.13653442090817
    max_kwh = 69.13231958480623
    timestamps, values = generate_energy_data(2016, building_id, min_kwh, max_kwh)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()