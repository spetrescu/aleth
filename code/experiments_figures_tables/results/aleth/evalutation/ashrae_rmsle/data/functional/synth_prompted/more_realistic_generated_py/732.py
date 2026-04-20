#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year: int, building_id: int,
                         min_val: float, max_val: float,
                         base: float, daily_amp: float, seasonal_amp: float,
                         noise_std: float):
    random.seed(42)
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        day_of_year = ts.timetuple().tm_yday
        hour_of_day = ts.hour
        sin_daily = math.sin(2 * math.pi * hour_of_day / 24)
        sin_seasonal = math.sin(2 * math.pi * day_of_year / 366)
        val = (base +
               daily_amp * sin_daily +
               seasonal_amp * sin_seasonal +
               random.gauss(0, noise_std))
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
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Building 732')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 732
    start_year = 2016
    min_val = 34.79342093491877
    max_val = 50.4343496013211
    base = 42.0
    daily_amp = 5.0
    seasonal_amp = 5.0
    noise_std = 0.5

    timestamps, values = generate_energy_data(
        start_year, building_id, min_val, max_val,
        base, daily_amp, seasonal_amp, noise_std
    )

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()
</CODE END>