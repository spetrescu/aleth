#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, min_kwh: float, max_kwh: float):
    random.seed(42)
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    hours_in_year = 366 * 24
    timestamps = []
    values = []
    for i in range(hours_in_year):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Daily pattern: amplitude 20 kWh
        daily = 20 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal pattern: amplitude 10 kWh
        seasonal = 10 * math.sin(2 * math.pi * (day_of_year - 1) / 365)
        base = 170
        noise = random.uniform(-2, 2)
        value = base + daily + seasonal + noise
        # Clip to bounds
        value = max(min_kwh, min(max_kwh, value))
        timestamps.append(ts)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.3f}'])
    return csv_path

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    # Format x-axis
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 899
    min_kwh = 139.7805343263447
    max_kwh = 206.0746637969271
    timestamps, values = generate_data(2016, building_id, min_kwh, max_kwh)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to {csv_path}')
    print(f'Plot saved to {png_path}')

if __name__ == "__main__":
    main()