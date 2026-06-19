#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    end = datetime.datetime(2016, 12, 31, 23, 0)

    timestamps = []
    values = []

    base = 26.5
    daily_amp = 3.0
    seasonal_amp = 2.0
    noise_std = 0.5
    min_val = 21.83959409727762
    max_val = 31.76871634529725

    current = start
    while current <= end:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday

        daily_cycle = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_cycle = seasonal_amp * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, noise_std)

        value = base + daily_cycle + seasonal_cycle + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current)
        values.append(value)

        current += datetime.timedelta(hours=1)

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
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(timestamps, values, linewidth=0.5)
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Energy (kWh)')
    ax.set_title('Hourly Energy Metering for Building 997')
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close(fig)

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '997.csv')
    png_path = os.path.join('generated_plots', '997.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()