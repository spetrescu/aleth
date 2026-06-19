#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year: int, hours: int, min_val: float, max_val: float):
    data = []
    start_dt = datetime(start_year, 1, 1, 0, 0)
    for i in range(hours):
        dt = start_dt + timedelta(hours=i)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday

        # Daily pattern: higher during day, lower at night
        daily = 10 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal pattern: slight variation over the year
        seasonal = 5 * math.sin(2 * math.pi * day_of_year / 365)

        base = 50 + daily + seasonal

        # Add random noise
        noise = random.uniform(-2, 2)

        value = base + noise

        # Clamp to specified bounds
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val

        timestamp_str = dt.strftime("%Y-%m-%dT%H:%M")
        data.append((timestamp_str, value))
    return data

def save_csv(filepath: str, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        writer.writerows(data)

def plot_data(filepath: str, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    timestamps = [datetime.strptime(row[0], "%Y-%m-%dT%H:%M") for row in data]
    values = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    random.seed(42)

    building_id = 682
    min_energy = 40.46044203476045
    max_energy = 60.840926235492525

    # 1 year of hourly data: 365 days * 24 hours = 8760 hours
    hours_in_year = 365 * 24

    data = generate_hourly_data(2016, hours_in_year, min_energy, max_energy)

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(csv_path, data)
    plot_data(png_path, data)

if __name__ == "__main__":
    main()