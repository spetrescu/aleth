#!/usr/bin/env python3
import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BUILDING_ID = 129
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_hourly_data(start_year: int, seed: int = 42):
    random.seed(seed)
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    end = datetime(start_year + 1, 1, 1, 0, 0)
    delta = timedelta(hours=1)

    timestamps = []
    values = []

    # Base consumption in kWh
    base = 90.0
    # Seasonal amplitude (higher in winter, lower in summer)
    seasonal_amp = 10.0
    # Daily pattern amplitude
    daily_amp = 5.0

    current = start
    hour_index = 0
    while current < end:
        # Seasonal component: sine wave over the year
        day_of_year = current.timetuple().tm_yday
        seasonal = seasonal_amp * \
            (1 + mdates.sin(2 * mdates.pi * day_of_year / 365.25))
        # Daily component: higher during day, lower at night
        hour_of_day = current.hour
        daily = daily_amp * \
            (1 + mdates.sin(2 * mdates.pi * hour_of_day / 24))
        # Random noise
        noise = random.uniform(-2.0, 2.0)
        value = base + seasonal + daily + noise
        # Clamp to given bounds
        value = max(72.99762908099157, min(111.4520871599569, value))

        timestamps.append(current.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

        current += delta
        hour_index += 1

    return timestamps, values

def save_csv(timestamps, values, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Convert timestamp strings back to datetime for plotting
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]

    plt.figure(figsize=(12, 6))
    plt.plot(dates, values, linewidth=0.5)
    plt.title(f"Energy Metering Data for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.grid(True)

    # Format x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def main():
    timestamps, values = generate_hourly_data(2016)
    save_csv(timestamps, values, CSV_PATH)
    plot_data(timestamps, values, PNG_PATH)

if __name__ == "__main__":
    main()