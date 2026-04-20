#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, start_date, end_date, start_val, end_val, seed=42):
    random.seed(seed)
    total_seconds = int((end_date - start_date).total_seconds())
    total_hours = total_seconds // 3600 + 1
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start_date + datetime.timedelta(hours=i)
        timestamps.append(ts)
        # Linear interpolation between start_val and end_val
        base = start_val + (end_val - start_val) * i / (total_hours - 1)
        # Add small Gaussian noise
        noise = random.gauss(0, 0.5)
        val = base + noise
        # Clip to bounds
        val = max(min(val, end_val), start_val)
        values.append(val)
    return timestamps, values

def save_csv(building_id, timestamps, values, directory):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, f"{building_id}.csv")
    with open(filepath, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])
    return filepath

def plot_data(building_id, timestamps, values, directory):
    os.makedirs(directory, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Value (kWh)')
    plt.title(f'Energy Metering Data for Building {building_id}')
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    filepath = os.path.join(directory, f"{building_id}.png")
    plt.savefig(filepath, dpi=300)
    plt.close()
    return filepath

def main():
    building_id = 969
    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    end_date = datetime.datetime(2016, 12, 31, 23, 0)  # 2016 is a leap year
    start_val = 134.82010567132244
    end_val = 195.3927979635897

    timestamps, values = generate_data(building_id, start_date, end_date, start_val, end_val)

    csv_dir = os.path.join('generated_data')
    png_dir = os.path.join('generated_plots')

    csv_path = save_csv(building_id, timestamps, values, csv_dir)
    png_path = plot_data(building_id, timestamps, values, png_dir)

    print(f"CSV saved to: {csv_path}")
    print(f"Plot saved to: {png_path}")

if __name__ == "__main__":
    main()