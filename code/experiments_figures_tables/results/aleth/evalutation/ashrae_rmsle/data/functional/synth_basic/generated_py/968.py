#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    start_dt = datetime(start_year, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for day in range(366):
        day_offset = random.uniform(-0.5, 0.5)  # seasonal variation
        for hour in range(24):
            ts = start_dt + timedelta(days=day, hours=hour)
            base = 8 + 2 * math.sin(2 * math.pi * hour / 24) + day_offset
            noise = random.uniform(-0.5, 0.5)
            value = base + noise
            if value < 0:
                value = 0.0
            timestamps.append(ts)
            values.append(round(value, 3))

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), val])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Sensor 968')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 968
    start_year = 2016
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    timestamps, values = generate_data(start_year, building_id)
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()
</CODE END>