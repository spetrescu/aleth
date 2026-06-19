#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    total_hours = 365 * 24  # 1 year
    timestamps = []
    values = []

    base = 40.5  # base consumption
    daily_amp = 4.5
    weekly_amp = 2.0

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # 0=Monday, 6=Sunday

        # Daily pattern: peak at noon
        daily = daily_amp * math.sin(2 * math.pi * (hour_of_day - 12) / 24)

        # Weekly pattern: lower on weekends
        weekly = weekly_amp * math.sin(2 * math.pi * (day_of_week - 3) / 7)
        if day_of_week >= 5:  # Saturday, Sunday
            weekly -= 1.5

        noise = random.uniform(-0.5, 0.5)

        value = base + daily + weekly + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Energy Metering for Building 1170')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 1170
    min_val = 33.72584944627759
    max_val = 48.949814328870836

    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)

    data_dir = 'generated_data'
    plot_dir = 'generated_plots'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, f'{building_id}.csv')
    png_path = os.path.join(plot_dir, f'{building_id}.png')

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == '__main__':
    main()