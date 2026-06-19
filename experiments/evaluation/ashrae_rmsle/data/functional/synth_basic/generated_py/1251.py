#!/usr/bin/env python3
import os
import csv
import datetime
import math
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 236.11484631841765
MAX_VAL = 348.8301252374236
BUILDING_ID = 1251
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []
    for i in range(hours_in_year):
        ts = start + datetime.timedelta(hours=i)
        timestamps.append(ts)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Base value
        val = 290.0
        # Daily variation
        val += 20.0 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal variation
        val += 30.0 * math.sin(2 * math.pi * day_of_year / 366)
        # Random noise
        val += random.gauss(0, 5)
        # Clamp to bounds
        val = max(MIN_VAL, min(MAX_VAL, val))
        values.append(val)
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
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
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