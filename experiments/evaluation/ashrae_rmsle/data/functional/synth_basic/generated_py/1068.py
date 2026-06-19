#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

MIN_VAL = 76.57015951226816
MAX_VAL = 110.8247923178868
BUILDING_ID = 1068
START_YEAR = 2016
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"

def generate_hourly_data(start_dt, hours):
    timestamps = []
    values = []
    for i in range(hours):
        dt = start_dt + timedelta(hours=i)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday
        # Daily sinusoidal pattern (peak during day)
        daily = 10 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal sinusoidal pattern (peak in mid-year)
        seasonal = 5 * math.sin(2 * math.pi * day_of_year / 365)
        base = 90 + daily + seasonal
        noise = random.gauss(0, 2)
        value = base + noise
        value = max(MIN_VAL, min(MAX_VAL, value))
        timestamps.append(dt.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    # Convert timestamps to matplotlib date format
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.plot(dates, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    random.seed(42)
    start_dt = datetime(START_YEAR, 1, 1, 0, 0)
    # 2016 is a leap year
    hours_in_year = 366 * 24
    timestamps, values = generate_hourly_data(start_dt, hours_in_year)
    csv_path = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
    png_path = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()