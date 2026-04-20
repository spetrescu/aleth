#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 18.457067465845377
MAX_VAL = 28.024147644271117
BUILDING_ID = 1216
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 24 * 366  # 2016 is a leap year
    timestamps = []
    values = []

    base = (MIN_VAL + MAX_VAL) / 2
    daily_amp = (MAX_VAL - MIN_VAL) * 0.2
    seasonal_amp = (MAX_VAL - MIN_VAL) * 0.1

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        timestamps.append(ts)

        # Daily cycle
        hour_of_day = i % 24
        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle
        day_of_year = i // 24
        seasonal_cycle = math.sin(2 * math.pi * day_of_year / 366)

        # Random noise
        noise = random.uniform(-0.05, 0.05) * (MAX_VAL - MIN_VAL)

        value = base + daily_amp * daily_cycle + seasonal_amp * seasonal_cycle + noise
        value = max(MIN_VAL, min(MAX_VAL, value))
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
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
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