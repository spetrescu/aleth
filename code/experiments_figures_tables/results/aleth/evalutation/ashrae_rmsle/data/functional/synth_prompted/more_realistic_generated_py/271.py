#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year=2016, building_id=271,
                  min_val=79.16730997325888, max_val=118.86862784050068):
    random.seed(42)
    start = datetime(start_year, 1, 1, 0, 0)
    end = datetime(start_year, 12, 31, 23, 0)
    delta = timedelta(hours=1)

    timestamps = []
    values = []

    current = start
    while current <= end:
        hour = current.hour
        day_of_year = current.timetuple().tm_yday

        # Daily sinusoidal pattern
        daily = 20 * math.sin(2 * math.pi * hour / 24)
        # Seasonal sinusoidal pattern
        seasonal = 10 * math.sin(2 * math.pi * day_of_year / 365)

        base = 100 + daily + seasonal
        noise = random.gauss(0, 2)
        value = base + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current)
        values.append(value)

        current += delta

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{building_id}.csv'
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

    # Format x-axis
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    png_path = f'generated_plots/{building_id}.png'
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 271
    timestamps, values = generate_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to {csv_path}')
    print(f'Plot saved to {png_path}')

if __name__ == "__main__":
    main()