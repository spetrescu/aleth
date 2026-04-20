#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 25.310011862475058
MAX_VAL = 37.15377461520831
BUILDING_ID = 1351
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    # 2016 is a leap year: 366 days
    total_hours = 366 * 24
    timestamps = []
    values = []
    base = (MIN_VAL + MAX_VAL) / 2
    amplitude = (MAX_VAL - MIN_VAL) / 2
    for i in range(total_hours):
        current = start + datetime.timedelta(hours=i)
        hour_of_day = i % 24
        day_of_year = i // 24
        daily_factor = math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_factor = math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, amplitude * 0.05)
        val = base + amplitude * (0.5 * daily_factor + 0.3 * seasonal_factor) + noise
        val = max(MIN_VAL, min(MAX_VAL, val))
        timestamps.append(current.strftime("%Y-%m-%dT%H:%M"))
        values.append(val)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    dates = [datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, marker='o', linestyle='-', markersize=2)
    plt.title(f"Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)
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