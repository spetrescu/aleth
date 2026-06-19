#!/usr/bin/env python3
import os
import csv
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year=2016, seed=42):
    random.seed(seed)
    # Base daily pattern (kWh per hour)
    base_pattern = []
    for hour in range(24):
        if 0 <= hour <= 5:
            base_pattern.append(0.02)
        elif 6 <= hour <= 8:
            base_pattern.append(0.03)
        elif 9 <= hour <= 17:
            base_pattern.append(0.04)
        elif 18 <= hour <= 20:
            base_pattern.append(0.03)
        else:  # 21-23
            base_pattern.append(0.02)

    # Generate timestamps and values
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []
    for day in range(365):
        for hour in range(24):
            ts = start + datetime.timedelta(days=day, hours=hour)
            base_val = base_pattern[hour]
            noise = random.gauss(0, 0.005)  # small noise
            val = base_val + noise
            if val < 0.001:
                val = 0.001
            timestamps.append(ts)
            values.append(val)

    # Scale to target total energy between given bounds
    total_current = sum(values)
    target_total = random.uniform(238.1810427990577, 362.9880485248807)
    scale_factor = target_total / total_current
    values = [v * scale_factor for v in values]
    return timestamps, values

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
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Sensor 110')
    plt.grid(True)
    # Format x-axis with month locator
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_hourly_data()
    csv_path = os.path.join('generated_data', '110.csv')
    png_path = os.path.join('generated_plots', '110.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()