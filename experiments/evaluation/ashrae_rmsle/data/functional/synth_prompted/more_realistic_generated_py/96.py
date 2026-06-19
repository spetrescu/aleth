#!/usr/bin/env python3
import os
import csv
import datetime
import math
import random
import matplotlib.pyplot as plt

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(hours):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday - 1  # zero‑based

        base = 0.02
        daily_amp = 0.01
        seasonal_amp = 0.005
        noise = random.gauss(0, 0.001)

        val = (
            base
            + daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
            + seasonal_amp * math.sin(2 * math.pi * day_of_year / 366)
            + noise
        )
        if val < 0:
            val = 0.0

        timestamps.append(ts)
        values.append(val)

    current_sum = sum(values)
    target_sum = random.uniform(258.028559740033, 373.0091122189639)
    scale = target_sum / current_sum
    values = [v * scale for v in values]

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
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Energy Metering Data for Building 96')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '96.csv')
    png_path = os.path.join('generated_plots', '96.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()