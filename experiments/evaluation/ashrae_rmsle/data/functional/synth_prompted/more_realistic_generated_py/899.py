import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_timestamps(start_year: int, hours: int):
    start = datetime(start_year, 1, 1, 0, 0)
    return [start + timedelta(hours=i) for i in range(hours)]

def generate_values(timestamps, target_total):
    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday  # 1-366 for leap year
        # Base consumption pattern
        base = 0.15
        amplitude_day = 0.05
        amplitude_season = 0.02
        day_pattern = amplitude_day * math.sin(2 * math.pi * hour_of_day / 24)
        season_pattern = amplitude_season * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, 0.01)
        value = base + day_pattern + season_pattern + noise
        if value < 0:
            value = 0.0
        values.append(value)
    # Scale to match target total
    current_total = sum(values)
    scale = target_total / current_total
    values = [v * scale for v in values]
    return values

def save_csv(file_path, timestamps, values):
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(file_path, timestamps, values):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering for Building 899')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

def main():
    random.seed(42)
    building_id = 899
    start_year = 2016
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = generate_timestamps(start_year, hours_in_year)
    target_total = 170.0  # kWh
    values = generate_values(timestamps, target_total)

    data_dir = 'generated_data'
    plot_dir = 'generated_plots'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, f'{building_id}.csv')
    png_path = os.path.join(plot_dir, f'{building_id}.png')

    save_csv(csv_path, timestamps, values)
    plot_data(png_path, timestamps, values)

if __name__ == "__main__":
    main()