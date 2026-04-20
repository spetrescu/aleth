#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    base = (min_val + max_val) / 2.0
    amplitude = (max_val - min_val) / 4.0
    noise = 0.02

    start = datetime(start_year, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(total_hours):
        current = start + timedelta(hours=i)
        hour_of_day = current.hour
        daily_pattern = math.sin(2 * math.pi * hour_of_day / 24.0)
        value = base + amplitude * daily_pattern + random.uniform(-noise, noise)
        value = max(min_val, min(max_val, value))
        timestamps.append(current)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 566
    min_val = 0.4428668712941868
    max_val = 0.6325883810554593
    timestamps, values = generate_data(2016, building_id, min_val, max_val)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()