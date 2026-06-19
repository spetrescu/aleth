#!/usr/bin/env python3

import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(building_id, start_year, min_total, max_total):
    random.seed(42)

    # Determine number of hours in the year (leap year check)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    end_date = datetime.datetime(start_year + 1, 1, 1, 0, 0)
    total_hours = int((end_date - start_date).total_seconds() // 3600)

    # Generate base pattern with daily sinusoidal variation and noise
    base_pattern = []
    for hour in range(total_hours):
        hour_of_day = hour % 24
        base = 0.5 + 0.5 * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.uniform(-0.05, 0.05)
        value = base + noise
        value = max(value, 0.01)  # Ensure positivity
        base_pattern.append(value)

    sum_base = sum(base_pattern)

    # Choose a deterministic total within the specified range
    target_total = random.uniform(min_total, max_total)

    # Scale base pattern to match the target total
    scale_factor = target_total / sum_base
    hourly_values = [v * scale_factor for v in base_pattern]

    # Generate timestamps
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(total_hours)]

    return timestamps, hourly_values

def save_csv(building_id, timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(building_id, timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, '-', linewidth=0.5)
    plt.title(f'Energy Metering for Sensor {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig(os.path.join('generated_plots', f'{building_id}.png'), dpi=300)
    plt.close()

def main():
    building_id = 1073
    start_year = 2016
    min_total = 147.84277822125432
    max_total = 218.3440494165181

    timestamps, values = generate_energy_data(building_id, start_year, min_total, max_total)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)

if __name__ == "__main__":
    main()