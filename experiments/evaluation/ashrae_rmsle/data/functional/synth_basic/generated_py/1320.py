#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    # Parameters
    building_id = 1320
    start_year = 2016
    start_date = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    num_hours = 366 * 24  # 8784 hours

    # Energy range in kWh
    min_total = 103.195682129826
    max_total = 153.1960118101345
    target_total = (min_total + max_total) / 2  # deterministic target

    # Base hourly consumption in kWh
    base = 0.0146
    amplitude = 0.003
    noise_std = 0.001

    random.seed(42)

    timestamps = []
    values = []

    for i in range(num_hours):
        ts = start_date + timedelta(hours=i)
        hour_of_day = ts.hour
        daily_variation = amplitude * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.gauss(0, noise_std)
        value = base + daily_variation + noise
        # Clip to realistic bounds
        value = max(0.005, min(0.025, value))
        timestamps.append(ts)
        values.append(value)

    # Scale to match target total
    current_total = sum(values)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

    return timestamps, values, building_id

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
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    timestamps, values, building_id = generate_data()
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()