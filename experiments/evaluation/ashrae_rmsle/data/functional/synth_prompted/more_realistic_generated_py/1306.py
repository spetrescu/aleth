#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    # 2016 is a leap year
    days_in_year = 366
    hours_in_year = days_in_year * 24

    base = 60.0  # base consumption in kWh
    daily_amp = 10.0  # daily variation amplitude
    seasonal_amp = 5.0  # seasonal variation amplitude
    noise_std = 2.0  # standard deviation of noise

    timestamps = []
    values = []

    start_time = datetime(start_year, 1, 1, 0, 0)

    for hour_idx in range(hours_in_year):
        current_time = start_time + timedelta(hours=hour_idx)
        hour_of_day = hour_idx % 24
        day_of_year = hour_idx // 24

        # Daily sinusoidal pattern: lower at night, higher during day
        daily_variation = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal sinusoidal pattern: higher in winter, lower in summer
        seasonal_variation = seasonal_amp * math.sin(2 * math.pi * day_of_year / days_in_year)

        noise = random.gauss(0, noise_std)

        value = base + daily_variation + seasonal_variation + noise
        # Clamp to realistic bounds
        value = max(55.07842489060558, min(80.97658914625595, value))

        timestamps.append(current_time)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Consumption for Building 1306')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.grid(True, linestyle='--', alpha=0.5)

    # Format x-axis with month labels
    locator = mdates.MonthLocator()
    formatter = mdates.DateFormatter('%b %Y')
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 1306
    start_year = 2016
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    timestamps, values = generate_energy_data(start_year, building_id)
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()