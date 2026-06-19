#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_data():
    random.seed(42)
    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for hour in range(total_hours):
        ts = start_date + datetime.timedelta(hours=hour)
        # Daily cycle
        daily = math.sin(2 * math.pi * (hour % 24) / 24)
        # Weekly cycle
        weekly = math.sin(2 * math.pi * hour / (24 * 7))
        # Seasonal cycle (yearly)
        seasonal = math.sin(2 * math.pi * hour / (24 * 366))
        base = 180.0
        noise = random.uniform(-5, 5)
        val = base + 20 * daily + 10 * weekly + 15 * seasonal + noise
        val = max(min(val, 217.51535916586468), 150.82548942901101)
        timestamps.append(ts.strftime('%Y-%m-%dT%H:%M'))
        values.append(val)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    # Convert timestamps to datetime objects for plotting
    times = [datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M') for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(times, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '219.csv')
    png_path = os.path.join('generated_plots', '219.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()