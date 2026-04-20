#!/usr/bin/env python3
import os
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 55.07842489060558
MAX_VAL = 80.97658914625595
BUILDING_ID = 1306
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_hourly_data():
    start = datetime.datetime(2016, 1, 1, 0, 0)
    end = datetime.datetime(2016, 12, 31, 23, 0)
    delta = datetime.timedelta(hours=1)

    timestamps = []
    values = []

    dt = start
    while dt <= end:
        hour = dt.hour
        day_of_year = dt.timetuple().tm_yday

        # Daily pattern: higher during day, lower at night
        daily = 10 * math.sin(2 * math.pi * hour / 24)

        # Seasonal variation: slight change over the year
        seasonal = 5 * math.sin(2 * math.pi * day_of_year / 366)

        # Base consumption around 70 kWh
        base = 70 + daily + seasonal

        # Random noise
        noise = random.gauss(0, 2)

        value = base + noise
        value = max(MIN_VAL, min(MAX_VAL, value))

        timestamps.append(dt.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

        dt += delta

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w") as f:
        f.write("timestamp,value\n")
        for ts, val in zip(timestamps, values):
            f.write(f"{ts},{val:.6f}\n")

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    dates = [datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]

    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    random.seed(0)
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()