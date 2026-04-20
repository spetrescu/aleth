#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 3.1045006490874725
MAX_VAL = 4.92825011172312
BASE_VAL = 4.0
AMPLITUDE = 0.5
NOISE_STD = 0.1
BUILDING_ID = 252
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        current = start + datetime.timedelta(hours=i)
        hour_of_day = current.hour
        # Daily sinusoidal pattern
        daily_pattern = math.sin(2 * math.pi * hour_of_day / 24)
        # Random noise
        noise = random.uniform(-NOISE_STD, NOISE_STD)
        value = BASE_VAL + AMPLITUDE * daily_pattern + noise
        # Clip to bounds
        value = max(MIN_VAL, min(MAX_VAL, value))
        timestamps.append(current)
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
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
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