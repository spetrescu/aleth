#!/usr/bin/env python3

import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt

def generate_data(building_id: int, start_year: int = 2016,
                  min_value: float = 39.359701791817386,
                  max_value: float = 57.75300779360088,
                  seed: int = 42):
    random.seed(seed)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start_date + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        # Daily sinusoidal pattern centered at 48 kWh with amplitude 5 kWh
        daily_pattern = 48 + 5 * math.sin(2 * math.pi * hour_of_day / 24)
        # Add Gaussian noise
        noise = random.gauss(0, 1)
        value = daily_pattern + noise
        # Clip to specified bounds
        value = max(min_value, min(max_value, value))
        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(building_id: int, timestamps, values, directory: str = 'generated_data'):
    os.makedirs(directory, exist_ok=True)
    csv_path = os.path.join(directory, f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(building_id: int, timestamps, values, directory: str = 'generated_plots'):
    os.makedirs(directory, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    png_path = os.path.join(directory, f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 701
    timestamps, values = generate_data(building_id)
    csv_path = save_csv(building_id, timestamps, values)
    png_path = plot_data(building_id, timestamps, values)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()