#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt

MIN_VALUE = 41.72725207430283
MAX_VALUE = 61.81480574188071
BASE_VALUE = (MIN_VALUE + MAX_VALUE) / 2

DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
BUILDING_ID = "979"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_hourly_data(start_year=2016):
    random.seed(42)
    data = []
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    end = datetime.datetime(start_year + 1, 1, 1, 0, 0)
    delta = datetime.timedelta(hours=1)
    current = start
    while current < end:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday
        # Daily pattern: higher during day, lower at night
        daily_variation = 5 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal pattern: slight variation over the year
        seasonal_variation = 5 * math.sin(2 * math.pi * day_of_year / 366)
        # Random noise
        noise = random.uniform(-0.5, 0.5)
        value = BASE_VALUE + daily_variation + seasonal_variation + noise
        # Clamp to min/max
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        data.append((current.strftime("%Y-%m-%dT%H:%M"), value))
        current += delta
    return data

def save_csv(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        writer.writerows(data)

def plot_data(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    timestamps = [datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M") for row in data]
    values = [row[1] for row in data]
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title("Hourly Energy Metering")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def main():
    data = generate_hourly_data()
    save_csv(data, CSV_PATH)
    plot_data(data, PNG_PATH)

if __name__ == "__main__":
    main()