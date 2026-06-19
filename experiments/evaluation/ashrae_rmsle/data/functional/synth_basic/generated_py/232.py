#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

MIN_VAL = 73.32320764914938
MAX_VAL = 109.05139223121135
BUILDING_ID = 232
START_DATE = datetime(2016, 1, 1, 0, 0)
TOTAL_HOURS = 365 * 24  # 1 year

def generate_data():
    random.seed(0)
    timestamps = []
    values = []
    mid = (MIN_VAL + MAX_VAL) / 2
    amplitude = (MAX_VAL - MIN_VAL) / 4
    noise_range = 0.05 * (MAX_VAL - MIN_VAL)

    for hour in range(TOTAL_HOURS):
        ts = START_DATE + timedelta(hours=hour)
        hour_of_day = ts.hour
        base = mid + amplitude * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.uniform(-noise_range, noise_range)
        val = base + noise
        val = max(MIN_VAL, min(MAX_VAL, val))
        timestamps.append(ts)
        values.append(val)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{BUILDING_ID}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {BUILDING_ID}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(f'generated_plots/{BUILDING_ID}.png', dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()