#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year=2016, building_id=1069, seed=42):
    random.seed(seed)
    # Define bounds
    min_val = 5.105624919200002
    max_val = 7.7571077830915
    base = 6.0
    daily_amp = 1.0
    seasonal_amp = 0.5
    noise_std = 0.1

    # Start and end dates
    start_dt = datetime(start_year, 1, 1, 0, 0)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    end_dt = start_dt + timedelta(days=days_in_year) - timedelta(hours=1)

    timestamps = []
    values = []

    current_dt = start_dt
    while current_dt <= end_dt:
        hour_of_day = current_dt.hour
        day_of_year = current_dt.timetuple().tm_yday

        # Daily pattern: higher during day, lower at night
        daily_pattern = math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal pattern: higher in winter, lower in summer
        seasonal_pattern = math.sin(2 * math.pi * day_of_year / days_in_year)

        # Random noise
        noise = random.gauss(0, noise_std)

        value = base + daily_amp * daily_pattern + seasonal_amp * seasonal_pattern + noise
        # Clip to bounds
        value = max(min_val, min(max_val, value))

        timestamps.append(current_dt)
        values.append(value)

        current_dt += timedelta(hours=1)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime('%Y-%m-%dT%H:%M')
            writer.writerow([ts_str, f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 1069
    timestamps, values = generate_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()