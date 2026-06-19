#!/usr/bin/env python3
import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 582.5378024899746
MAX_VAL = 873.9468486655253
BUILDING_ID = 560
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    # 2016 is a leap year: 366 days
    total_hours = 366 * 24
    timestamps = [start + datetime.timedelta(hours=i) for i in range(total_hours)]

    base = (MAX_VAL + MIN_VAL) / 2
    daily_amplitude = 50.0
    yearly_amplitude = 100.0
    noise_std = 10.0

    values = []
    for ts in timestamps:
        # Daily cycle
        daily = math.sin(2 * math.pi * ts.hour / 24) * daily_amplitude
        # Yearly cycle
        day_of_year = ts.timetuple().tm_yday - 1  # 0-based
        yearly = math.sin(2 * math.pi * day_of_year / 366) * yearly_amplitude
        # Random noise
        noise = random.gauss(0, noise_std)
        val = base + daily + yearly + noise
        # Clip to bounds
        val = max(MIN_VAL, min(MAX_VAL, val))
        values.append(val)
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

    # Format x-axis with dates
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)
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