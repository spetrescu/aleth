#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

MIN_TOTAL = 237.9327205920052
MAX_TOTAL = 355.9878017691312
BUILDING_ID = 788
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_timestamps(start_year: int):
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year: 366 days * 24 hours = 8784 hours
    total_hours = 366 * 24
    return [start + timedelta(hours=i) for i in range(total_hours)]

def generate_values(timestamps):
    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        # Base pattern: sinusoidal variation between 0.02 and 0.04 kWh
        base = 0.03 + 0.01 * math.sin(2 * math.pi * hour_of_day / 24)
        # Add small Gaussian noise
        noise = random.gauss(0, 0.002)
        val = max(0.0, base + noise)
        values.append(val)
    return values

def scale_values(values, target_total):
    current_sum = sum(values)
    if current_sum == 0:
        return values
    factor = target_total / current_sum
    return [round(v * factor, 6) for v in values]

def write_csv(timestamps, values):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Sensor {BUILDING_ID}")
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    random.seed(42)
    timestamps = generate_timestamps(2016)
    raw_values = generate_values(timestamps)
    target_total = random.uniform(MIN_TOTAL, MAX_TOTAL)
    scaled_values = scale_values(raw_values, target_total)
    write_csv(timestamps, scaled_values)
    plot_data(timestamps, scaled_values)

if __name__ == "__main__":
    main()