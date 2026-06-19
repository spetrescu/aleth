#!/usr/bin/env python3
import csv
import os
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, sensor_id: int, min_val: float, max_val: float):
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days = 366 if is_leap else 365
    total_hours = days * 24

    start_dt = datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start_dt + timedelta(hours=i)
        timestamps.append(ts)
        values.append(random.uniform(min_val, max_val))

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Sensor 674')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    random.seed(42)
    sensor_id = 674
    min_val = 83.38888980830478
    max_val = 123.126893724599

    timestamps, values = generate_data(2016, sensor_id, min_val, max_val)

    csv_path = f'generated_data/{sensor_id}.csv'
    png_path = f'generated_plots/{sensor_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()