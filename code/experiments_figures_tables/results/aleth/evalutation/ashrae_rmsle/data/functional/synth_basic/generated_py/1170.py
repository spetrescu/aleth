#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    mid_val = (min_val + max_val) / 2.0
    daily_amp = 3.0
    seasonal_amp = 2.0
    noise_amp = 0.5

    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year, 12, 31, 23, 0)
    delta = timedelta(hours=1)

    timestamps = []
    values = []

    current_dt = start_dt
    while current_dt <= end_dt:
        hour = current_dt.hour
        day_of_year = current_dt.timetuple().tm_yday

        daily_component = daily_amp * math.sin(2 * math.pi * hour / 24)
        seasonal_component = seasonal_amp * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.uniform(-noise_amp, noise_amp)

        value = mid_val + daily_component + seasonal_component + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current_dt)
        values.append(value)

        current_dt += delta

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 1170
    min_val = 33.72584944627759
    max_val = 48.949814328870836
    start_year = 2016

    timestamps, values = generate_energy_data(start_year, building_id, min_val, max_val)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)

    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()