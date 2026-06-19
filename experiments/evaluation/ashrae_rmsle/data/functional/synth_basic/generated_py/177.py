#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Constants
BUILDING_ID = 177
MIN_VALUE = 275.5305868649695
MAX_VALUE = 398.1825857676519
START_DATE = datetime(2016, 1, 1, 0, 0)
HOURS_IN_YEAR = 365 * 24  # 2016 is not a leap year
CSV_DIR = "generated_data"
PNG_DIR = "generated_plots"
CSV_PATH = os.path.join(CSV_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PNG_DIR, f"{BUILDING_ID}.png")

def generate_hourly_data():
    random.seed(42)
    data = []
    for i in range(HOURS_IN_YEAR):
        ts = START_DATE + timedelta(hours=i)
        # Day of year (1-365)
        day_of_year = ts.timetuple().tm_yday
        # Seasonal component: sinusoidal over the year
        seasonal = math.sin(2 * math.pi * day_of_year / 365)
        # Daily component: higher during day, lower at night
        hour = ts.hour
        daily = math.sin(2 * math.pi * hour / 24)
        # Base value between min and max
        base = (MIN_VALUE + MAX_VALUE) / 2
        amplitude = (MAX_VALUE - MIN_VALUE) / 2
        value = base + amplitude * seasonal * 0.5 + amplitude * daily * 0.3
        # Add small random noise
        noise = random.gauss(0, 5)
        value += noise
        # Clip to bounds
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        data.append((ts, value))
    return data

def save_csv(data):
    os.makedirs(CSV_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, value in data:
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{value:.6f}"])

def plot_data(data):
    os.makedirs(PNG_DIR, exist_ok=True)
    timestamps, values = zip(*data)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    data = generate_hourly_data()
    save_csv(data)
    plot_data(data)

if __name__ == "__main__":
    main()