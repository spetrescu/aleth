import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 25.310011862475058
MAX_VAL = 37.15377461520831
BASE_CONSUMPTION = 30.0
DAILY_AMPLITUDE = 5.0
WEEKEND_REDUCTION = 2.0
WINTER_ADDITION = 2.0
NOISE_STD = 0.5

BUILDING_ID = "1351"
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_hourly_data(start_year=2016):
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []
    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        hour = ts.hour
        day_of_week = ts.weekday()  # 0=Mon, 6=Sun
        month = ts.month

        # Daily sinusoidal pattern
        daily_variation = DAILY_AMPLITUDE * math.sin(2 * math.pi * hour / 24)

        # Weekend reduction
        weekend_variation = -WEEKEND_REDUCTION if day_of_week >= 5 else 0.0

        # Seasonal addition for winter months
        seasonal_variation = WINTER_ADDITION if month in (12, 1, 2) else 0.0

        # Random noise
        noise = random.uniform(-NOISE_STD, NOISE_STD)

        value = (BASE_CONSUMPTION + daily_variation +
                 weekend_variation + seasonal_variation + noise)

        # Clip to bounds
        value = max(min(value, MAX_VAL), MIN_VAL)

        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PLOT_DIR, exist_ok=True)
    # Convert timestamp strings back to datetime for plotting
    times = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]

    plt.figure(figsize=(12, 6))
    plt.plot(times, values, linewidth=0.5)
    plt.title(f"Hourly Energy Consumption for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.grid(True)

    # Format x-axis with month labels
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
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