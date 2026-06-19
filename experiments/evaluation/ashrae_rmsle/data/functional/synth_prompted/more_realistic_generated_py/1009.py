#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt

MIN_VAL = 22.408721470871683
MAX_VAL = 34.23071102102833
BASE = 28.0
DAILY_AMPLITUDE = 3.0
SEASONAL_AMPLITUDE = 2.0
NOISE_STD = 0.5
BUILDING_ID = 1009
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = [start + datetime.timedelta(hours=i) for i in range(hours_in_year)]
    values = []

    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_pattern = DAILY_AMPLITUDE * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_pattern = SEASONAL_AMPLITUDE * math.sin(2 * math.pi * (day_of_year - 1) / 366)
        noise = random.gauss(0, NOISE_STD)

        value = BASE + daily_pattern + seasonal_pattern + noise
        value = max(MIN_VAL, min(MAX_VAL, value))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()