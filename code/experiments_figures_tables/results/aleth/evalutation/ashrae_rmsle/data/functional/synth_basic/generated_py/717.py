#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BUILDING_ID = 717
START_YEAR = 2016
CSV_DIR = "generated_data"
PNG_DIR = "generated_plots"
CSV_PATH = os.path.join(CSV_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PNG_DIR, f"{BUILDING_ID}.png")
MIN_VALUE = 7.717369210259385
MAX_VALUE = 11.47934358582655
TOTAL_HOURS = 365 * 24  # 1 year, non-leap

def generate_data():
    random.seed(42)
    start = datetime.datetime(START_YEAR, 1, 1, 0, 0)
    timestamps = []
    values = []
    for i in range(TOTAL_HOURS):
        ts = start + datetime.timedelta(hours=i)
        hour = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Daily pattern: higher during day, lower at night
        daily_cycle = 2 * math.sin(2 * math.pi * hour / 24)
        # Seasonal pattern: slight variation over the year
        seasonal_cycle = 0.5 * math.sin(2 * math.pi * day_of_year / 365)
        base = 9 + daily_cycle + seasonal_cycle
        noise = random.gauss(0, 0.3)
        value = base + noise
        # Clip to bounds
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        timestamps.append(ts)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(CSV_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PNG_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
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