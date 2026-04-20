#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    timestamps = []
    values = []
    for day in range(366):  # 2016 is a leap year
        day_of_year = day + 1
        for hour in range(24):
            ts = start + datetime.timedelta(days=day, hours=hour)
            timestamps.append(ts)
            hour_of_day = hour
            base = 51.5
            daily = 5 * math.sin(2 * math.pi * hour_of_day / 24)
            seasonal = 5 * math.sin(2 * math.pi * (day_of_year - 1) / 366)
            noise = random.uniform(-1, 1)
            value = base + daily + seasonal + noise
            value = max(min(value, 61.81480574188071), 41.72725207430283)
            values.append(value)
    return timestamps, values

def save_csv(timestamps, values, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(timestamps, values, linewidth=0.5)
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Energy (kWh)')
    ax.set_title('Hourly Energy Metering')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(path)
    plt.close(fig)

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '979.csv')
    png_path = os.path.join('generated_plots', '979.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()