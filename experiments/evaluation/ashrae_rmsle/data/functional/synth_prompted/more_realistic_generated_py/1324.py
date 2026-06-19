#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)

    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year, 12, 31, 23, 0)
    total_hours = int((end_dt - start_dt).total_seconds() // 3600) + 1

    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        current_dt = start_dt + timedelta(hours=hour_offset)
        timestamps.append(current_dt.strftime('%Y-%m-%dT%H:%M'))

        # Daily cycle: higher during day, lower at night
        hour_of_day = current_dt.hour
        daily_variation = 5.0 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle over the year
        day_of_year = current_dt.timetuple().tm_yday
        seasonal_variation = 2.0 * math.sin(2 * math.pi * day_of_year / 366)

        base = 37.5 + daily_variation + seasonal_variation
        noise = random.gauss(0, 0.5)

        value = base + noise
        value = max(min_val, min(max_val, value))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = [datetime.strptime(ts, '%Y-%m-%dT%H:%M') for ts in timestamps]
    plt.plot(dates, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True, linestyle='--', alpha=0.5)

    # Format x-axis with month labels
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate(rotation=45)

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 1324
    min_val = 29.63284192186316
    max_val = 44.86818723891756

    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)

    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()