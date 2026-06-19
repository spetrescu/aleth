#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year=2016, building_id=1216,
                  min_val=18.457067465845377, max_val=28.024147644271117,
                  seed=42):
    random.seed(seed)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    end = datetime.datetime(start_year, 12, 31, 23, 0)
    delta = datetime.timedelta(hours=1)

    timestamps = []
    values = []

    base = (min_val + max_val) / 2.0
    amp_daily = 2.0
    amp_seasonal = 3.0
    noise_std = 0.5

    ts = start
    while ts <= end:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24.0)
        seasonal_cycle = math.sin(2 * math.pi * day_of_year / 365.0)
        noise = random.gauss(0, noise_std)

        value = base + amp_daily * daily_cycle + amp_seasonal * seasonal_cycle + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(ts)
        values.append(value)

        ts += delta

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
    plt.title(f'Energy Metering {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 1216
    timestamps, values = generate_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()