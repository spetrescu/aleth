#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)
    start = datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    base = 57.0
    amp_daily = 5.0
    amp_seasonal = 3.0
    noise_std = 0.5

    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        hour = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily pattern: peak at 14:00
        daily = amp_daily * math.sin(2 * math.pi * (hour - 14) / 24)

        # Seasonal pattern: peak at day 172 (approx June 21)
        seasonal = amp_seasonal * math.sin(2 * math.pi * (day_of_year - 172) / 366)

        noise = random.gauss(0, noise_std)

        value = base + daily + seasonal + noise
        # Clip to the specified range
        if value < 47.18137787927474:
            value = 47.18137787927474
        elif value > 67.93624526061862:
            value = 67.93624526061862

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linestyle='-', marker='o', markersize=1, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '693.csv')
    png_path = os.path.join('generated_plots', '693.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()