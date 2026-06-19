#!/usr/bin/env python3
import os
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_hourly_data(start_year: int, building_id: int, min_total: float, max_total: float):
    random.seed(0)
    # Generate timestamps for one year hourly
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    timestamps = [start_dt + datetime.timedelta(hours=i) for i in range(24 * 365)]
    # Base pattern generation
    base_values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Daily pattern
        daily = 0.5 + 0.3 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal pattern
        seasonal = 0.1 * math.sin(2 * math.pi * day_of_year / 365)
        # Random noise
        noise = random.gauss(0, 0.05)
        value = daily + seasonal + noise
        base_values.append(value)
    # Scale to target total
    target_total = random.uniform(min_total, max_total)
    sum_base = sum(base_values)
    scale = target_total / sum_base
    scaled_values = [v * scale for v in base_values]
    return timestamps, scaled_values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write('timestamp,value\n')
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime('%Y-%m-%dT%H:%M')
            f.write(f'{ts_str},{val:.6f}\n')

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Building 1220')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 1220
    min_total = 430.84003323375
    max_total = 647.4830280297615
    timestamps, values = generate_hourly_data(2016, building_id, min_total, max_total)
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()