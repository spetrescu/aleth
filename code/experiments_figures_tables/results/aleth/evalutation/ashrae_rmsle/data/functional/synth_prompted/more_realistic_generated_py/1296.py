#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year=2016, building_id=1296,
                         min_val=12.728388395912841, max_val=18.6549444635869,
                         seed=42):
    random.seed(seed)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    base = (min_val + max_val) / 2
    daily_amp = 2.0
    seasonal_amp = 1.5
    noise_std = 0.3

    timestamps = []
    values = []

    start_dt = datetime(start_year, 1, 1, 0, 0)
    for hour in range(total_hours):
        current_dt = start_dt + timedelta(hours=hour)
        hour_of_day = current_dt.hour
        day_of_year = current_dt.timetuple().tm_yday

        daily_component = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_component = seasonal_amp * math.sin(2 * math.pi * day_of_year / days_in_year)
        noise = random.gauss(0, noise_std)

        value = base + daily_component + seasonal_component + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current_dt.strftime("%Y-%m-%dT%H:%M"))
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

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 1296
    timestamps, values = generate_energy_data(building_id=building_id)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()