#!/usr/bin/env python3
import os
import csv
import random
import datetime
import matplotlib.pyplot as plt

def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []

    range_val = max_val - min_val
    amplitude = range_val / 2
    offset = min_val + amplitude

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        # Daily sinusoidal pattern
        base = offset + amplitude * math.sin(2 * math.pi * hour_of_day / 24)
        # Add Gaussian noise
        noise = random.gauss(0, 0.005)
        val = base + noise
        # Clamp to bounds
        val = max(min_val, min(max_val, val))
        timestamps.append(ts)
        values.append(val)

    return timestamps, values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.12f}"])

def plot_data(timestamps, values, filepath: str, building_id: int):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 636
    min_val = 0.14810220115103379
    max_val = 0.2212414366651684
    timestamps, values = generate_data(2016, building_id, min_val, max_val)
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path, building_id)

if __name__ == "__main__":
    import math
    main()