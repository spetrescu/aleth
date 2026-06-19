#!/usr/bin/env python3
import os
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday  # 1-366

        # Daily cycle: amplitude 1.5 kWh
        daily = 1.5 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal cycle: amplitude 0.5 kWh
        seasonal = 0.5 * math.sin(2 * math.pi * day_of_year / 366)

        base = 9.5 + daily + seasonal
        noise = random.gauss(0, 0.05)
        value = base + noise

        # Clamp to the specified range
        min_val = 7.717369210259385
        max_val = 11.47934358582655
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('timestamp,value\n')
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime('%Y-%m-%dT%H:%M')
            f.write(f'{ts_str},{val:.6f}\n')

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering (2016)')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '717.csv')
    png_path = os.path.join('generated_plots', '717.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()