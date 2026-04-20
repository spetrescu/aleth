#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt

def generate_data():
    random.seed(42)
    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = []
    raw_values = []

    for i in range(hours_in_year):
        current_time = start_date + datetime.timedelta(hours=i)
        hour_of_day = i % 24
        day_of_year = i // 24

        # Base consumption pattern with daily and yearly sinusoidal variations
        base = (
            0.015
            + 0.005 * math.sin(2 * math.pi * hour_of_day / 24)
            + 0.003 * math.sin(2 * math.pi * day_of_year / 366)
        )
        noise = random.uniform(-0.001, 0.001)
        value = max(base + noise, 0.0)

        timestamps.append(current_time)
        raw_values.append(value)

    # Scale values to match a realistic total energy consumption
    total_raw = sum(raw_values)
    target_total = random.uniform(104.07884286200516, 148.41377507272665)
    scale_factor = target_total / total_raw
    scaled_values = [v * scale_factor for v in raw_values]

    return timestamps, scaled_values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '589.csv')
    png_path = os.path.join('generated_plots', '589.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()