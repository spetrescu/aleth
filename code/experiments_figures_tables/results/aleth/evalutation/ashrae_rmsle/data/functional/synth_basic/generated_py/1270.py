#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 9.19515035005519
MAX_VAL = 13.591230701261837
MID_VAL = (MIN_VAL + MAX_VAL) / 2
AMPLITUDE = (MAX_VAL - MIN_VAL) / 2

BUILDING_ID = "1270"
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime(2016, 1, 1, 0, 0)
    # 2016 is a leap year: 366 days
    total_hours = 366 * 24
    timestamps = []
    values = []
    for hour in range(total_hours):
        ts = start + timedelta(hours=hour)
        hour_of_day = ts.hour
        # Daily sinusoidal pattern
        daily_factor = math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal sinusoidal pattern over the year
        day_of_year = ts.timetuple().tm_yday
        seasonal_factor = math.sin(2 * math.pi * day_of_year / 366)
        base = MID_VAL + AMPLITUDE * daily_factor + (AMPLITUDE / 4) * seasonal_factor
        noise = random.uniform(-0.1, 0.1)
        value = base + noise
        # Clamp to bounds
        value = max(MIN_VAL, min(MAX_VAL, value))
        timestamps.append(ts)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)
    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()