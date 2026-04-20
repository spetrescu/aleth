#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_data(start_year=2016, building_id=252, min_val=3.1045006490874725, max_val=4.92825011172312):
    random.seed(42)
    # Determine if start year is leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    timestamps = []
    values = []

    base_time = datetime(start_year, 1, 1, 0, 0)
    for hour in range(total_hours):
        current_time = base_time + timedelta(hours=hour)
        timestamps.append(current_time.strftime("%Y-%m-%dT%H:%M"))

        # Daily cycle: higher during day, lower at night
        hour_of_day = current_time.hour
        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle: variation over the year
        day_of_year = current_time.timetuple().tm_yday
        seasonal_cycle = math.sin(2 * math.pi * day_of_year / days_in_year)

        # Parameters for realistic variation
        mean_val = (min_val + max_val) / 2
        amplitude_daily = 0.5
        amplitude_seasonal = 0.3
        noise = random.gauss(0, 0.05)

        raw_value = mean_val + amplitude_daily * daily_cycle + amplitude_seasonal * seasonal_cycle + noise
        # Clip to bounds
        value = max(min_val, min(max_val, raw_value))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    output_dir = os.path.join("generated_data")
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])
    return csv_path

def plot_data(timestamps, values, building_id):
    output_dir = os.path.join("generated_plots")
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, f"{building_id}.png")

    # Convert timestamps to matplotlib date format
    times = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]

    plt.figure(figsize=(12, 4))
    plt.plot(times, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 252
    timestamps, values = generate_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f"CSV saved to: {csv_path}")
    print(f"Plot saved to: {png_path}")

if __name__ == "__main__":
    main()