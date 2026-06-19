#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 23.54284746182003
MAX_VAL = 34.70707132418707
BUILDING_ID = 1096
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    end = start + datetime.timedelta(days=366)  # 2016 is a leap year
    timestamps = []
    values = []
    current = start
    while current < end:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday
        # Daily pattern: higher during day, lower at night
        daily = 5 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal variation over the year
        seasonal = 2 * math.sin(2 * math.pi * day_of_year / 366)
        base = 29.124 + daily + seasonal
        noise = random.gauss(0, 0.5)
        value = base + noise
        # Clamp to bounds
        value = max(MIN_VAL, min(MAX_VAL, value))
        timestamps.append(current)
        values.append(value)
        current += datetime.timedelta(hours=1)
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
    fig, ax = plt.subplots(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    ax.plot_date(dates, values, linestyle='solid', marker=None)
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Energy (kWh)")
    ax.set_title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close(fig)

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()