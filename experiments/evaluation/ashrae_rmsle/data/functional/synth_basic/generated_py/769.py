#!/usr/bin/env python3
import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt

def generate_data(building_id: int, start_year: int, hours: int):
    random.seed(42)
    start_date = datetime.datetime(start_year, 1, 1)
    timestamps = []
    raw_values = []

    # Generate raw hourly values with a daily sinusoidal pattern
    for i in range(hours):
        ts = start_date + datetime.timedelta(hours=i)
        timestamps.append(ts)
        hour_of_day = ts.hour
        # Base consumption around 0.01 kWh with daily variation
        base = 0.01
        amplitude = 0.005
        daily_variation = amplitude * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.uniform(-0.001, 0.001)
        value = base + daily_variation + noise
        raw_values.append(value)

    # Scale to target total energy between the given bounds
    target_total = random.uniform(70.98632052247326, 106.12105859199765)
    raw_sum = sum(raw_values)
    scale_factor = target_total / raw_sum
    scaled_values = [v * scale_factor for v in raw_values]

    return timestamps, scaled_values, target_total

def save_csv(building_id: int, timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(building_id: int, timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 769
    start_year = 2016
    # 365 days * 24 hours
    hours = 365 * 24
    timestamps, values, total = generate_data(building_id, start_year, hours)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)
    print(f'Data generated for building {building_id}.')
    print(f'Total energy: {total:.6f} kWh')
    print('CSV and PNG files saved.')

if __name__ == "__main__":
    main()