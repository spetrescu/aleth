#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    avg_val = (min_val + max_val) / 2.0
    amplitude_daily = 1.5
    amplitude_weekly = 0.5
    amplitude_seasonal = 0.5
    noise_std = 0.2

    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # Monday=0
        day_of_year = ts.timetuple().tm_yday

        daily_variation = amplitude_daily * math.sin(2 * math.pi * hour_of_day / 24.0)
        weekly_variation = amplitude_weekly * math.sin(2 * math.pi * day_of_week / 7.0)
        seasonal_variation = amplitude_seasonal * math.sin(2 * math.pi * day_of_year / 365.0)
        noise = random.gauss(0, noise_std)

        value = avg_val + daily_variation + weekly_variation + seasonal_variation + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    output_dir = os.path.join("generated_data")
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id: int):
    output_dir = os.path.join("generated_plots")
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, f"{building_id}.png")

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Consumption for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 1182
    min_val = 9.354406038557231
    max_val = 14.046482289758368
    start_year = 2016

    timestamps, values = generate_energy_data(start_year, building_id, min_val, max_val)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()