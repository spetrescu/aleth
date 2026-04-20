#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int,
                         building_id: int,
                         min_total: float,
                         max_total: float,
                         seed: int = 42):
    random.seed(seed)

    # Parameters for realistic hourly pattern
    base = 0.05          # base consumption in kWh
    daily_amp = 0.02     # daily amplitude
    seasonal_amp = 0.01  # seasonal amplitude
    noise_std = 0.003    # standard deviation of noise

    # Phases (deterministic)
    daily_phase = 0.0
    seasonal_phase = 0.0

    # Generate timestamps for one year (non-leap year)
    start = datetime(start_year, 1, 1, 0, 0)
    timestamps = [start + timedelta(hours=i) for i in range(365 * 24)]

    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_component = base + daily_amp * math.sin(2 * math.pi * hour_of_day / 24 + daily_phase)
        seasonal_component = seasonal_amp * math.sin(2 * math.pi * day_of_year / 365 + seasonal_phase)
        noise = random.gauss(0, noise_std)

        value = daily_component + seasonal_component + noise
        value = max(value, 0.0)  # ensure non-negative
        values.append(value)

    current_total = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

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
    png_path = os.path.join('generated_plots', f'{building_id}.png')

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 641
    min_total = 341.4948580015958
    max_total = 510.1096354288321
    start_year = 2016

    timestamps, values = generate_energy_data(start_year, building_id, min_total, max_total)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)

    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()