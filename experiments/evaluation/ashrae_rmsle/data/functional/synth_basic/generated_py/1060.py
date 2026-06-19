#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt

MIN_VAL = 32.90561464535022
MAX_VAL = 47.39962262839086
MEAN_VAL = (MIN_VAL + MAX_VAL) / 2
AMPLITUDE = (MAX_VAL - MIN_VAL) / 2 * 0.9  # keep base within bounds
RANDOM_SEED = 42

DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
BUILDING_ID = "1060"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_hourly_data(start_year=2016):
    """Generate hourly timestamps and realistic energy values for one year."""
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start_date + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        # Daily sinusoidal pattern
        base = MEAN_VAL + AMPLITUDE * math.sin(2 * math.pi * hour_of_day / 24)
        # Add random noise
        noise = random.gauss(0, 1)
        value = base + noise
        # Clip to allowed range
        if value < MIN_VAL:
            value = MIN_VAL
        elif value > MAX_VAL:
            value = MAX_VAL
        timestamps.append(ts)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title("Hourly Energy Metering")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def main():
    random.seed(RANDOM_SEED)
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values, CSV_PATH)
    plot_data(timestamps, values, PNG_PATH)

if __name__ == "__main__":
    main()