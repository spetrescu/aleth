#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    hours_in_year = 366 * 24
    timestamps = [start + timedelta(hours=i) for i in range(hours_in_year)]
    values = []

    base = 180.0  # base energy value in kWh
    daily_amp = 20.0
    seasonal_amp = 10.0
    noise_std = 5.0
    min_val = 147.84277822125432
    max_val = 218.3440494165181

    for ts in timestamps:
        hour = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily pattern: peak at noon
        daily_pattern = daily_amp * math.sin(2 * math.pi * (hour - 6) / 24)

        # Seasonal pattern: peak around day 172 (summer)
        seasonal_pattern = seasonal_amp * math.sin(2 * math.pi * (day_of_year - 80) / 365)

        noise = random.gauss(0, noise_std)

        value = base + daily_pattern + seasonal_pattern + noise
        value = max(min_val, min(max_val, value))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with date labels
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 1073
    start_year = 2016

    timestamps, values = generate_energy_data(start_year, building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)

    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()