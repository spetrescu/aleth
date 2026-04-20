#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

MIN_VAL = 23.4912342606076
MAX_VAL = 33.769162238313434
RANGE_VAL = MAX_VAL - MIN_VAL
BUILDING_ID = 204
START_DATE = datetime(2016, 1, 1, 0, 0)
TOTAL_HOURS = 365 * 24  # 1 year

def generate_data():
    random.seed(42)
    timestamps = []
    values = []
    for i in range(TOTAL_HOURS):
        current_time = START_DATE + timedelta(hours=i)
        hour_of_day = current_time.hour
        # Daily sinusoidal pattern: low at midnight, high at noon
        pattern = 0.5 * (1 + math.sin(2 * math.pi * hour_of_day / 24 - math.pi / 2))
        base = MIN_VAL + RANGE_VAL * pattern
        noise = random.uniform(-0.5, 0.5)
        value = base + noise
        # Clamp to bounds
        value = max(MIN_VAL, min(MAX_VAL, value))
        timestamps.append(current_time.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = f"generated_data/{BUILDING_ID}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs("generated_plots", exist_ok=True)
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    png_path = f"generated_plots/{BUILDING_ID}.png"
    plt.savefig(png_path)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()