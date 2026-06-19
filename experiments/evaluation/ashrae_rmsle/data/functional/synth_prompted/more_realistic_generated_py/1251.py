#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(building_id, start_year, total_hours, min_total, max_total, seed=42):
    random.seed(seed)
    base_consumption = 0.033  # kWh per hour average
    timestamps = []
    raw_values = []

    start_time = datetime(start_year, 1, 1, 0, 0)
    for i in range(total_hours):
        ts = start_time + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # Monday=0, Sunday=6
        month = ts.month

        # Daily variation: peak at noon
        daily_factor = 0.2 * math.sin(2 * math.pi * (hour_of_day - 6) / 24)

        # Weekly variation: lower on weekends
        weekly_factor = -0.1 if day_of_week >= 5 else 0.0

        # Seasonal variation: slightly higher in winter months
        seasonal_factor = 0.05 if month in (12, 1, 2) else 0.0

        # Random noise
        noise_factor = random.gauss(0, 0.05)

        # Total factor
        factor = 1 + daily_factor + weekly_factor + seasonal_factor + noise_factor
        if factor < 0.1:
            factor = 0.1  # prevent negative or too low values

        value = base_consumption * factor
        timestamps.append(ts)
        raw_values.append(value)

    # Scale to target total energy
    raw_sum = sum(raw_values)
    target_total = random.uniform(min_total, max_total)
    scale = target_total / raw_sum
    scaled_values = [v * scale for v in raw_values]

    return timestamps, scaled_values, target_total

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Consumption')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 1251
    start_year = 2016
    # 2016 is a leap year: 366 days
    total_hours = 366 * 24
    min_total = 236.11484631841765
    max_total = 348.8301252374236

    timestamps, values, target_total = generate_energy_data(
        building_id, start_year, total_hours, min_total, max_total, seed=42
    )

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

    print(f'Generated CSV: {csv_path}')
    print(f'Generated PNG: {png_path}')
    print(f'Target total energy: {target_total:.3f} kWh')

if __name__ == "__main__":
    main()