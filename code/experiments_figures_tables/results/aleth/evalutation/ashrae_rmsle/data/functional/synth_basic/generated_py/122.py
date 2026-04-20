#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year: int, total_hours: int, min_total: float, max_total: float, seed: int = 42):
    random.seed(seed)
    base_pattern = []
    for hour in range(24):
        base = 1.5 + 0.5 * math.sin(2 * math.pi * hour / 24)
        base_pattern.append(base)

    values = []
    for i in range(total_hours):
        hour_of_day = i % 24
        base = base_pattern[hour_of_day]
        noise = random.uniform(-0.2, 0.2)
        val = max(base + noise, 0.0)
        values.append(val)

    current_sum = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / current_sum
    values = [v * scale_factor for v in values]
    return values

def create_timestamps(start_date: datetime, total_hours: int):
    timestamps = []
    for i in range(total_hours):
        ts = start_date + timedelta(hours=i)
        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
    return timestamps

def save_csv(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.3f}"])

def plot_data(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig(file_path)
    plt.close()

def main():
    building_id = 122
    start_year = 2016
    start_date = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    min_total = 225.79135326380492
    max_total = 340.01029088598057

    values = generate_hourly_data(start_year, total_hours, min_total, max_total)
    timestamps = create_timestamps(start_date, total_hours)

    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"

    save_csv(csv_path, timestamps, values)
    plot_data(png_path, timestamps, values)

if __name__ == "__main__":
    main()