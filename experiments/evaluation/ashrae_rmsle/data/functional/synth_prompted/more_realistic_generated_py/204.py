#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

MIN_VAL = 23.4912342606076
MAX_VAL = 33.769162238313434
MEAN_VAL = (MIN_VAL + MAX_VAL) / 2
AMPLITUDE = (MAX_VAL - MIN_VAL) / 2
NOISE_STD = 0.2  # standard deviation of Gaussian noise

START_DATE = datetime(2016, 1, 1, 0, 0)
END_DATE = datetime(2016, 12, 31, 23, 0)

CSV_PATH = os.path.join("generated_data", "204.csv")
PNG_PATH = os.path.join("generated_plots", "204.png")

def generate_hourly_data():
    random.seed(42)
    timestamps = []
    values = []
    current = START_DATE
    while current <= END_DATE:
        hour_of_day = current.hour
        # Daily sinusoidal pattern
        daily_pattern = math.sin(2 * math.pi * hour_of_day / 24)
        base = MEAN_VAL + AMPLITUDE * daily_pattern
        # Add small Gaussian noise
        noisy = base + random.gauss(0, NOISE_STD)
        # Clip to min/max
        value = max(MIN_VAL, min(MAX_VAL, noisy))
        timestamps.append(current.strftime("%Y-%m-%dT%H:%M"))
        values.append(round(value, 6))
        current += timedelta(hours=1)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, val])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    # Convert timestamps to datetime objects for plotting
    times = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(times, values, linewidth=0.5)
    plt.title("Hourly Energy Metering (kWh)")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()