#!/usr/bin/env python3
import csv
import math
import os
import random
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def generate_hourly_data(start_year: int, hours: int, seed: int = 42):
    random.seed(seed)
    base_value = 62.5  # mid-point of the range
    daily_amp = 5.0    # daily variation amplitude
    seasonal_amp = 3.0 # seasonal variation amplitude
    noise_std = 0.5    # standard deviation of noise

    start = datetime(start_year, 1, 1)
    timestamps = []
    values = []

    for i in range(hours):
        current = start + timedelta(hours=i)
        # Daily cycle: 24-hour sine wave
        daily_cycle = math.sin(2 * math.pi * (i % 24) / 24)
        # Seasonal cycle: 365-day sine wave
        seasonal_cycle = math.sin(2 * math.pi * i / (24 * 365))
        # Random noise
        noise = random.gauss(0, noise_std)

        value = (
            base_value
            + daily_amp * daily_cycle
            + seasonal_amp * seasonal_cycle
            + noise
        )
        # Clamp to realistic range
        value = max(50.052529975278645, min(74.71295290550637, value))

        timestamps.append(current)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    # 2016 is a leap year: 366 days * 24 hours = 8784 hours
    hours_in_year = 366 * 24
    timestamps, values = generate_hourly_data(2016, hours_in_year)

    csv_path = os.path.join('generated_data', '1000.csv')
    png_path = os.path.join('generated_plots', '1000.png')

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()