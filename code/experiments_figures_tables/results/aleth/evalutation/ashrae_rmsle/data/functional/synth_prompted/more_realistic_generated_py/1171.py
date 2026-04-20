#!/usr/bin/env python3
import csv
import datetime
import math
import os
import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year=2016, building_id=1171,
                  min_val=120.78932088172101, max_val=175.58609375205714,
                  seed=42):
    random.seed(seed)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # non-leap year
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(hours_in_year)]
    values = []

    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # Monday=0
        day_of_year = ts.timetuple().tm_yday

        # Daily pattern: higher during day, lower at night
        daily = 20 * math.sin(2 * math.pi * hour_of_day / 24)

        # Weekly pattern: slightly lower on weekends
        weekly = 10 * math.sin(2 * math.pi * day_of_week / 7)

        # Seasonal pattern: small variation over the year
        seasonal = 5 * math.sin(2 * math.pi * day_of_year / 365)

        # Random noise
        noise = random.gauss(0, 2)

        value = 150 + daily + weekly + seasonal + noise
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
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%dT%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 1171
    timestamps, values = generate_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()