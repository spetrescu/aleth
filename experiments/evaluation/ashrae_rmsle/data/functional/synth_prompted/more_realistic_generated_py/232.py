#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year=2016, building_id=232,
                  min_value=73.32320764914938, max_value=109.05139223121135):
    random.seed(42)
    start = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # Monday=0
        day_of_year = ts.timetuple().tm_yday

        # Base consumption
        base = 90.0

        # Daily cycle: higher during day, lower at night
        daily = 10.0 * math.sin(2 * math.pi * hour_of_day / 24)

        # Weekly cycle: slightly lower on weekends
        weekly = 5.0 * math.sin(2 * math.pi * day_of_week / 7)

        # Seasonal cycle: slight variation over the year
        seasonal = 5.0 * math.sin(2 * math.pi * day_of_year / 365)

        # Random noise
        noise = random.gauss(0, 1)

        value = base + daily + weekly + seasonal + noise
        # Clip to specified bounds
        value = max(min_value, min(max_value, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with dates
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 232
    timestamps, values = generate_data(building_id=building_id)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()