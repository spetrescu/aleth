#!/usr/bin/env python3

import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(building_id, start_year, min_total, max_total):
    random.seed(42)
    start_dt = datetime(start_year, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(total_hours):
        dt = start_dt + timedelta(hours=i)
        hour_of_day = dt.hour
        base = 0.03 + 0.02 * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.uniform(-0.005, 0.005)
        value = max(0.0, base + noise)
        timestamps.append(dt)
        values.append(value)

    current_sum = sum(values)
    target_total = random.uniform(min_total, max_total)
    scaling_factor = target_total / current_sum
    values = [v * scaling_factor for v in values]

    return timestamps, values

def save_csv(building_id, timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for dt, val in zip(timestamps, values):
            writer.writerow([dt.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(building_id, timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 118
    start_year = 2016
    min_total = 281.20568570243233
    max_total = 412.00314903395713

    timestamps, values = generate_energy_data(building_id, start_year, min_total, max_total)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)

if __name__ == "__main__":
    main()