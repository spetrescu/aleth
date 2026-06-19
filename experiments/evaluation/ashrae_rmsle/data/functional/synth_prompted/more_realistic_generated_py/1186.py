#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 133.98870778211247
MAX_VAL = 199.75409982677175
BUILDING_ID = 1186
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")
START_DATE = datetime.datetime(2016, 1, 1, 0, 0)
HOURS_IN_YEAR = 365 * 24  # 2016 is not a leap year

def generate_data():
    random.seed(42)
    timestamps = []
    values = []
    base = (MIN_VAL + MAX_VAL) / 2.0
    amp_daily = 20.0
    amp_seasonal = 10.0
    noise_std = 5.0

    for i in range(HOURS_IN_YEAR):
        ts = START_DATE + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        sin_daily = math.sin(2 * math.pi * hour_of_day / 24.0)
        sin_seasonal = math.sin(2 * math.pi * day_of_year / 365.0)

        value = (
            base
            + amp_daily * sin_daily
            + amp_seasonal * sin_seasonal
            + random.gauss(0, noise_std)
        )
        value = max(MIN_VAL, min(MAX_VAL, value))

        timestamps.append(ts)
        values.append(value)

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
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
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