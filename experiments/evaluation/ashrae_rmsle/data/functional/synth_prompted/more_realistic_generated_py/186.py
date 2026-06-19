#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int):
    random.seed(42)

    # Define bounds
    min_val = 1.1917655751288687
    max_val = 1.853626057189711

    # Base value and amplitudes
    base = (min_val + max_val) / 2
    daily_amp = 0.2
    seasonal_amp = 0.2
    noise_std = 0.05

    # Prepare timestamps
    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year, 12, 31, 23, 0)
    delta = timedelta(hours=1)

    timestamps = []
    values = []

    current_dt = start_dt
    while current_dt <= end_dt:
        hour_of_day = current_dt.hour
        day_of_year = current_dt.timetuple().tm_yday

        # Daily cycle
        daily = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle
        seasonal = seasonal_amp * math.sin(2 * math.pi * day_of_year / 366)

        # Random noise
        noise = random.gauss(0, noise_std)

        value = base + daily + seasonal + noise
        # Clip to bounds
        value = max(min_val, min(max_val, value))

        timestamps.append(current_dt)
        values.append(value)

        current_dt += delta

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
    plt.ylabel('kWh')
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 186
    start_year = 2016

    timestamps, values = generate_energy_data(start_year, building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)

    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()