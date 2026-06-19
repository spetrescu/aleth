#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int):
    random.seed(42)

    # Parameters for realistic hourly consumption (kWh)
    base = 0.0125          # average hourly consumption
    amp_daily = 0.003      # daily variation amplitude
    amp_seasonal = 0.002   # seasonal variation amplitude
    noise_std = 0.0005     # random noise standard deviation
    weekend_factor = 0.9   # reduce consumption on weekends

    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        dt = start_dt + datetime.timedelta(hours=hour_offset)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday
        weekday = dt.weekday()  # 0=Mon, 6=Sun

        # Daily sinusoidal pattern
        daily_variation = amp_daily * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal sinusoidal pattern
        seasonal_variation = amp_seasonal * math.sin(2 * math.pi * day_of_year / 366)

        # Random noise
        noise = random.gauss(0, noise_std)

        value = base + daily_variation + seasonal_variation + noise

        if weekday >= 5:  # Saturday or Sunday
            value *= weekend_factor

        if value < 0:
            value = 0.0001

        timestamps.append(dt)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for dt, val in zip(timestamps, values):
            writer.writerow([dt.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates_num = mdates.date2num(timestamps)
    plt.plot_date(dates_num, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Sensor {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis to show month
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150)
    plt.close()

def main():
    building_id = 626
    start_year = 2016
    timestamps, values = generate_data(start_year, building_id)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()