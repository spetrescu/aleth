#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 47.18137787927474
MAX_VAL = 67.93624526061862
BASE = (MIN_VAL + MAX_VAL) / 2.0
AMPLITUDE_DAY = 5.0
AMPLITUDE_SEASON = 3.0
NOISE_STD = 0.5
BUILDING_ID = 693
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_hourly_data(start_year=2016):
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    end = datetime.datetime(start_year, 12, 31, 23, 0)
    delta = datetime.timedelta(hours=1)
    timestamps = []
    values = []
    current = start
    while current <= end:
        hour = current.hour
        month = current.month
        # Daily sinusoidal pattern
        daily = AMPLITUDE_DAY * math.sin(2 * math.pi * hour / 24)
        # Seasonal sinusoidal pattern
        seasonal = AMPLITUDE_SEASON * math.sin(2 * math.pi * (month - 1) / 12)
        noise = random.gauss(0, NOISE_STD)
        value = BASE + daily + seasonal + noise
        # Clip to bounds
        value = max(min(value, MAX_VAL), MIN_VAL)
        timestamps.append(current)
        values.append(value)
        current += delta
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.3f}"])

def plot_data(timestamps, values):
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    random.seed(42)
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()