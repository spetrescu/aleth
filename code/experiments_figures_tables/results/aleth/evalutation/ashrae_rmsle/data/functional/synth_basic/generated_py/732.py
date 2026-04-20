#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt

MIN_VAL = 34.79342093491877
MAX_VAL = 50.4343496013211
SENSOR_ID = 732
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{SENSOR_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{SENSOR_ID}.png")
HOURS_PER_YEAR = 365 * 24
RANDOM_SEED = 0
NOISE_STD = 1.5

def generate_hourly_data():
    random.seed(RANDOM_SEED)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    timestamps = []
    values = []
    for i in range(HOURS_PER_YEAR):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        # Daily sinusoidal pattern: low at night, high during day
        sin_val = math.sin(2 * math.pi * (hour_of_day - 6) / 24)
        base = MIN_VAL + (MAX_VAL - MIN_VAL) * (0.5 + 0.5 * sin_val)
        noise = random.gauss(0, NOISE_STD)
        val = base + noise
        # Clip to bounds
        val = max(MIN_VAL, min(MAX_VAL, val))
        timestamps.append(ts)
        values.append(val)
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
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Sensor {SENSOR_ID}")
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()