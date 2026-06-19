import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 23.54284746182003
MAX_VAL = 34.70707132418707
BUILDING_ID = 1096
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime(2016, 1, 1, 0, 0)
    end = datetime(2016, 12, 31, 23, 0)
    delta = timedelta(hours=1)

    timestamps = []
    values = []
    dt = start
    while dt <= end:
        hour = dt.hour
        day_of_year = dt.timetuple().tm_yday  # 1-366

        # Daily pattern: 0.5 + 0.3 * sin(2π*(hour-6)/24)
        daily_pattern = 0.5 + 0.3 * math.sin(2 * math.pi * (hour - 6) / 24)

        # Seasonal pattern: 0.5 + 0.1 * sin(2π*(day_of_year-80)/366)
        seasonal_pattern = 0.5 + 0.1 * math.sin(2 * math.pi * (day_of_year - 80) / 366)

        base = daily_pattern * seasonal_pattern  # 0.08 to 0.48 approx

        value = MIN_VAL + base * (MAX_VAL - MIN_VAL)

        # Add small Gaussian noise
        noise = random.gauss(0, 0.05 * (MAX_VAL - MIN_VAL))
        value += noise

        # Clip to bounds
        if value < MIN_VAL:
            value = MIN_VAL
        elif value > MAX_VAL:
            value = MAX_VAL

        timestamps.append(dt)
        values.append(value)

        dt += delta

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

    # Format x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()