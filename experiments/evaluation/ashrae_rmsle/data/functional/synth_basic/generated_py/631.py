#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, start_year, min_value, max_value, seed=42):
    random.seed(seed)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start_date + datetime.timedelta(hours=i)
        hour_of_day = i % 24
        # Daily sinusoidal pattern centered at 12.5 kWh with amplitude 2.5 kWh
        base = 12.5 + 2.5 * math.sin(2 * math.pi * hour_of_day / 24)
        # Add Gaussian noise
        noise = random.gauss(0, 0.2)
        val = base + noise
        # Clip to specified range
        val = max(min_value, min(max_value, val))
        timestamps.append(ts)
        values.append(val)
    return timestamps, values

def save_csv(building_id, timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{building_id}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(building_id, timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    # Format x-axis with month locator
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    png_path = f'generated_plots/{building_id}.png'
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 631
    start_year = 2016
    min_value = 10.462970339883046
    max_value = 14.974510562437139
    timestamps, values = generate_data(building_id, start_year, min_value, max_value)
    csv_path = save_csv(building_id, timestamps, values)
    png_path = plot_data(building_id, timestamps, values)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()