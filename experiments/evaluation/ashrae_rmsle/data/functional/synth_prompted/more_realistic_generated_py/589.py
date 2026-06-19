#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Constants
BUILDING_ID = 589
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")
START_DATE = datetime(2016, 1, 1, 0, 0)
END_DATE = datetime(2016, 12, 31, 23, 0)
MIN_VAL = 104.07884286200516
MAX_VAL = 148.41377507272665
BASE_VAL = 120.0
DAILY_AMP = 15.0
YEARLY_AMP = 10.0
NOISE_STD = 5.0
SEED = 42

def generate_hourly_data():
    random.seed(SEED)
    timestamps = []
    values = []
    current = START_DATE
    while current <= END_DATE:
        # Day of year (1-366)
        day_of_year = current.timetuple().tm_yday
        # Hour of day (0-23)
        hour_of_day = current.hour
        # Daily cycle
        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24)
        # Yearly cycle
        yearly_cycle = math.sin(2 * math.pi * day_of_year / 366)
        # Random noise
        noise = random.gauss(0, NOISE_STD)
        # Compute value
        val = (BASE_VAL +
               DAILY_AMP * daily_cycle +
               YEARLY_AMP * yearly_cycle +
               noise)
        # Clip to min/max
        val = max(MIN_VAL, min(MAX_VAL, val))
        timestamps.append(current)
        values.append(val)
        current += timedelta(hours=1)
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
    # Format x-axis with month labels
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()