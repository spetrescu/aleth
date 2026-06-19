#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    start_date = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start_date + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # Monday=0
        day_of_year = ts.timetuple().tm_yday  # 1-366

        base = 0.03  # base consumption in kWh
        daily_variation = 0.01 * math.sin(2 * math.pi * hour_of_day / 24)
        weekly_variation = 0.005 * math.sin(2 * math.pi * day_of_week / 7)
        seasonal_variation = 0.005 * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, 0.001)

        value = base + daily_variation + weekly_variation + seasonal_variation + noise
        if value < 0:
            value = 0.0

        timestamps.append(ts)
        values.append(value)

    # Scale to target total energy between given bounds
    target_total = random.uniform(281.20568570243233, 412.00314903395713)
    current_total = sum(values)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

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
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Energy consumption for building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis with month locator
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=150)
    plt.close()

def main():
    building_id = 118
    timestamps, values = generate_energy_data(start_year=2016, building_id=building_id)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()