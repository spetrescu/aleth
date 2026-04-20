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
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    base_mid = 57.7  # midpoint of the given range
    min_val = 46.81394521860747
    max_val = 68.88121218563275

    for i in range(hours_in_year):
        current = start + timedelta(hours=i)
        timestamps.append(current)

        # Seasonal adjustment based on month
        month = current.month - 1  # 0-11
        seasonal = 3 * math.sin(2 * math.pi * month / 12)

        # Daily variation
        hour_of_day = current.hour
        daily = 5 * math.sin(2 * math.pi * hour_of_day / 24)

        # Random noise
        noise = random.gauss(0, 0.5)

        value = base_mid + seasonal + daily + noise
        # Clip to the specified range
        value = max(min_val, min(max_val, value))
        values.append(value)

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
    plt.title('Hourly Energy Consumption')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '1111.csv')
    png_path = os.path.join('generated_plots', '1111.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()