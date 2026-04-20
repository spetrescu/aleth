#!/usr/bin/env python3
import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours = 366 * 24  # 2016 is a leap year
    timestamps = [start + datetime.timedelta(hours=i) for i in range(hours)]

    values = []
    for ts in timestamps:
        hour = ts.hour
        # Base consumption
        base = 0.03  # kWh per hour
        # Daily pattern: higher during day (6-21), lower at night
        factor = 1.2 if 6 <= hour < 22 else 0.8
        val = base * factor
        # Add small random noise
        val += random.uniform(-0.005, 0.005)
        values.append(val)

    # Scale to target sum within the given range
    target_sum = 300.0  # kWh, within [244.71, 362.96]
    current_sum = sum(values)
    scale = target_sum / current_sum
    values = [v * scale for v in values]

    return timestamps, values

def save_csv(timestamps, values, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, filepath):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, values = generate_data()

    os.makedirs('generated_data', exist_ok=True)
    os.makedirs('generated_plots', exist_ok=True)

    csv_path = os.path.join('generated_data', '1086.csv')
    png_path = os.path.join('generated_plots', '1086.png')

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()