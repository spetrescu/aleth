#!/usr/bin/env python3
import csv
import datetime
import math
import os
import random

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

MIN_VALUE = 22.408721470871683
MAX_VALUE = 34.23071102102833
BUILDING_ID = 1009
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

        # Daily pattern: higher during day, lower at night
        daily = 3 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal pattern: higher in winter, lower in summer
        seasonal = 2 * math.sin(2 * math.pi * day_of_year / 366)

        base = 28 + daily + seasonal
        noise = random.gauss(0, 0.5)
        value = base + noise
        value = max(MIN_VALUE, min(MAX_VALUE, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, "-", linewidth=0.5)
    plt.title(f"Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()