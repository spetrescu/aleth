#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year=2016,
                         min_val=170.333801583746,
                         max_val=247.8908416974116,
                         building_id=90):
    random.seed(42)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    start_dt = datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []

    base = 200.0
    daily_amp = 20.0
    seasonal_amp = 10.0
    noise_amp = 5.0

    for hour_idx in range(total_hours):
        ts = start_dt + timedelta(hours=hour_idx)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_variation = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_variation = seasonal_amp * math.sin(2 * math.pi * (day_of_year - 1) / days_in_year)
        noise = noise_amp * (random.random() * 2 - 1)

        value = base + daily_variation + seasonal_variation + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    # Convert timestamps to datetime objects for plotting
    dt_objects = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.plot(dt_objects, values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 90
    timestamps, values = generate_energy_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f"CSV saved to: {csv_path}")
    print(f"Plot saved to: {png_path}")

if __name__ == "__main__":
    main()