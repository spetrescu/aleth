#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year=2016,
                         days=365,
                         daily_min=227.23128787316068,
                         daily_max=328.5650526070966,
                         seed=42):
    random.seed(seed)
    # Prepare timestamps
    start_dt = datetime(start_year, 1, 1, 0, 0)
    timestamps = [start_dt + timedelta(hours=i) for i in range(days * 24)]
    values = []

    for day in range(days):
        # Daily total consumption
        daily_total = random.uniform(daily_min, daily_max)

        # Generate base hourly pattern
        hourly = []
        amplitude = 3.0  # kWh
        offset = 6       # peak at 12:00
        base = 5.0       # kWh
        for hour in range(24):
            # Sine wave pattern
            sin_val = math.sin(2 * math.pi * (hour - offset) / 24)
            val = base + amplitude * sin_val
            # Add random noise
            val += random.gauss(0, 0.5)
            # Ensure non-negative
            val = max(0.0, val)
            hourly.append(val)

        # Scale to match daily total
        sum_hourly = sum(hourly)
        if sum_hourly == 0:
            scale = 0
        else:
            scale = daily_total / sum_hourly
        scaled_hourly = [v * scale for v in hourly]
        values.extend(scaled_hourly)

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
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_hourly_data()
    csv_path = os.path.join('generated_data', '1391.csv')
    png_path = os.path.join('generated_plots', '1391.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()