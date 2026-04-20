#!/usr/bin/env python3
import os
import csv
import datetime
import math
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, start_year, min_val, max_val):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        timestamps.append(ts)
        # Base consumption
        base = 21.0
        # Daily pattern: higher during day
        daily = 3.0 * math.sin(2 * math.pi * (i % 24) / 24)
        # Seasonal pattern over the year
        seasonal = 2.0 * math.sin(2 * math.pi * i / (24 * 366))
        # Random noise
        noise = random.gauss(0, 0.5)
        val = base + daily + seasonal + noise
        # Clip to min and max
        val = max(min_val, min(max_val, val))
        values.append(val)
    return timestamps, values

def save_csv(building_id, timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{building_id}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(building_id, timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)
    plt.tight_layout()
    # Format x-axis dates
    plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    png_path = f'generated_plots/{building_id}.png'
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 522
    start_year = 2016
    min_val = 17.39358412431408
    max_val = 25.222707621942995
    timestamps, values = generate_data(building_id, start_year, min_val, max_val)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)

if __name__ == "__main__":
    main()