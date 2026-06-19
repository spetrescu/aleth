#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 60.23385383280047
MAX_VAL = 89.27666629873181
BUILDING_ID = 513
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_data(start_year=2016):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    end = datetime.datetime(start_year, 12, 31, 23, 0)
    delta = datetime.timedelta(hours=1)

    timestamps = []
    values = []

    current = start
    while current <= end:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday

        # Base daily sinusoidal pattern
        daily = (MIN_VAL + MAX_VAL) / 2 + (MAX_VAL - MIN_VAL) / 2 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal variation
        seasonal = 1 + 0.1 * math.sin(2 * math.pi * day_of_year / 366)

        base = daily * seasonal

        # Add small random noise
        noise = random.uniform(-0.5, 0.5)
        value = base + noise

        # Clamp to bounds
        if value < MIN_VAL:
            value = MIN_VAL
        elif value > MAX_VAL:
            value = MAX_VAL

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
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()