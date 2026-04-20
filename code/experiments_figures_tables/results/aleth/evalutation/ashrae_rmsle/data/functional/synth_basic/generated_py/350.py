#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)

    start = datetime(2016, 1, 1, 0, 0)
    hours_in_year = 8760  # 2016 is a leap year? 2016 is leap year, so 366 days * 24 = 8784
    # Adjust for leap year
    if start.year % 4 == 0 and (start.year % 100 != 0 or start.year % 400 == 0):
        hours_in_year = 366 * 24

    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start + timedelta(hours=i)
        timestamps.append(ts)

        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_pattern = math.sin(2 * math.pi * hour_of_day / 24) * 0.005
        seasonal_pattern = math.sin(2 * math.pi * day_of_year / 366) * 0.003
        noise = random.gauss(0, 0.001)

        value = 0.015 + daily_pattern + seasonal_pattern + noise
        if value < 0:
            value = 0.0
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with month labels
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '350.csv')
    png_path = os.path.join('generated_plots', '350.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()