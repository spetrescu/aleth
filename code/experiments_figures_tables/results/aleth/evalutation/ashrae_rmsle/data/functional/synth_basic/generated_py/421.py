#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt

def generate_data(building_id, start_year, min_val, max_val, output_csv, output_png):
    random.seed(42)

    # Create directories
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    os.makedirs(os.path.dirname(output_png), exist_ok=True)

    # Time range: one year starting from start_year-01-01 00:00
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    # Parameters for realistic pattern
    base = (min_val + max_val) / 2.0
    amplitude_daily = 3.0
    amplitude_seasonal = 2.0
    noise_std = 0.5

    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        dt = start_dt + datetime.timedelta(hours=hour_offset)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday  # 1-366

        daily_factor = math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_factor = math.sin(2 * math.pi * day_of_year / days_in_year)

        value = (base
                 + amplitude_daily * daily_factor
                 + amplitude_seasonal * seasonal_factor
                 + random.gauss(0, noise_std))

        # Clip to min and max
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val

        timestamps.append(dt)
        values.append(value)

    # Write CSV
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(output_png, dpi=300)
    plt.close()

def main():
    building_id = 421
    start_year = 2016
    min_val = 23.557394837295437
    max_val = 35.59328748179138
    output_csv = f'generated_data/{building_id}.csv'
    output_png = f'generated_plots/{building_id}.png'
    generate_data(building_id, start_year, min_val, max_val, output_csv, output_png)

if __name__ == "__main__":
    main()