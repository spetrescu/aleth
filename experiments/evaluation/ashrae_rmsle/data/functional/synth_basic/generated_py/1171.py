#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VALUE = 120.78932088172101
MAX_VALUE = 175.58609375205714
BUILDING_ID = 1171
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    base = (MIN_VALUE + MAX_VALUE) / 2
    amp_day = 20.0
    amp_year = 10.0
    noise_std = 2.0

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday - 1  # 0-indexed

        daily = amp_day * math.sin(2 * math.pi * hour_of_day / 24)
        yearly = amp_year * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, noise_std)

        value = base + daily + yearly + noise
        value = max(MIN_VALUE, min(MAX_VALUE, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PLOT_DIR, exist_ok=True)
    dates = mdates.date2num(timestamps)
    plt.figure(figsize=(12, 6))
    plt.plot_date(dates, values, linestyle='solid', marker=None)
    plt.title(f"Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
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