#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 43.629498481995476
MAX_VAL = 63.74054239460782
BASE = 53.7
AMPLITUDE = 5.0
NOISE_STD = 1.0
BUILDING_ID = 906
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []
    for i in range(total_hours):
        dt = start + datetime.timedelta(hours=i)
        hour_of_day = dt.hour
        daily_variation = AMPLITUDE * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.gauss(0, NOISE_STD)
        value = BASE + daily_variation + noise
        value = max(MIN_VAL, min(MAX_VAL, value))
        timestamps.append(dt)
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
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(timestamps, values, linewidth=0.5)
    ax.set_title(f"Energy Metering for Building {BUILDING_ID}")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Energy (kWh)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close(fig)

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()