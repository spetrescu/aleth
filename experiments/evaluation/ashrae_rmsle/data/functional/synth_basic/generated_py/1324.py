#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_hourly_data(start_year: int, building_id: int, min_val: float, max_val: float):
    # Determine if leap year
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(start_year, 12, 31, 23, 0, 0)
    total_hours = int((end_date - start_date).total_seconds() // 3600) + 1

    timestamps = []
    values = []

    for hour_index in range(total_hours):
        current_time = start_date + timedelta(hours=hour_index)
        timestamps.append(current_time)

        # Daily pattern: sinusoidal variation over 24 hours
        hour_of_day = current_time.hour
        daily_variation = 5.0 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal variation: sinusoidal over the year
        day_of_year = current_time.timetuple().tm_yday
        seasonal_variation = 2.0 * math.sin(2 * math.pi * day_of_year / 366)

        # Base value
        base = 37.25 + daily_variation + seasonal_variation

        # Random noise
        noise = random.uniform(-1.0, 1.0)

        value = base + noise
        # Clamp to min and max
        value = max(min_val, min(max_val, value))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Building 1324')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    random.seed(42)
    building_id = 1324
    min_val = 29.63284192186316
    max_val = 44.86818723891756
    start_year = 2016

    timestamps, values = generate_hourly_data(start_year, building_id, min_val, max_val)

    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    png_path = os.path.join('generated_plots', f'{building_id}.png')

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()