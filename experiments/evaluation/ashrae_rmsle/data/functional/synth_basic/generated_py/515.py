#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []

    base = 85.0
    daily_amp = 10.0
    seasonal_amp = 5.0
    noise_std = 2.0
    min_val = 68.73440374908921
    max_val = 102.46854488854834

    for hour_offset in range(total_hours):
        current = start_date + datetime.timedelta(hours=hour_offset)
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday

        daily_component = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_component = seasonal_amp * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, noise_std)

        value = base + daily_component + seasonal_component + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath, building_id):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot_date(timestamps, values, '-', linewidth=0.5)
    ax.set_title(f'Energy Metering Data for Building {building_id}')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Energy (kWh)')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close(fig)

def main():
    building_id = 515
    start_year = 2016
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    timestamps, values = generate_energy_data(start_year, building_id)
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path, building_id)

if __name__ == "__main__":
    main()