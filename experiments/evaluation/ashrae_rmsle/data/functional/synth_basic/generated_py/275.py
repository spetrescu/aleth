#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 118.28946765487859
MAX_VAL = 175.30554980163924
BUILDING_ID = 275
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        base = 150.0
        daily_variation = 20.0 * math.sin(2 * math.pi * hour_of_day / 24.0)
        seasonal_variation = 10.0 * math.sin(2 * math.pi * day_of_year / 365.0)
        noise = random.uniform(-5.0, 5.0)

        val = base + daily_variation + seasonal_variation + noise
        val = max(MIN_VAL, min(MAX_VAL, val))

        timestamps.append(ts)
        values.append(val)

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    dates = [mdates.date2num(ts) for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, marker='o', linestyle='-', markersize=2)
    plt.title(f'Energy Metering for Building {BUILDING_ID}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()