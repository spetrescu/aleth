#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 51.946693965093075
MAX_VAL = 76.32933375297397
BASE_VAL = (MIN_VAL + MAX_VAL) / 2
DAILY_AMPLITUDE = 5.0
WEEKLY_AMPLITUDE = 3.0
NOISE_AMPLITUDE = 1.0

DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, "1095.csv")
PNG_PATH = os.path.join(PLOT_DIR, "1095.png")

def generate_hourly_data(start_year=2016):
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    end = datetime.datetime(start_year, 12, 31, 23, 0)
    delta = datetime.timedelta(hours=1)
    timestamps = []
    values = []
    current = start
    while current <= end:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday
        daily_cycle = DAILY_AMPLITUDE * math.sin(2 * math.pi * hour_of_day / 24)
        weekly_cycle = WEEKLY_AMPLITUDE * math.sin(2 * math.pi * day_of_year / 7)
        noise = random.uniform(-NOISE_AMPLITUDE, NOISE_AMPLITUDE)
        value = BASE_VAL + daily_cycle + weekly_cycle + noise
        value = max(MIN_VAL, min(MAX_VAL, value))
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
    plt.title("Energy Metering 1095")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    random.seed(42)
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()