import csv
import math
import os
import random
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)

    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []

    base = (min_val + max_val) / 2.0

    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        timestamps.append(ts)

        day_of_year = ts.timetuple().tm_yday
        hour_of_day = ts.hour

        # Seasonal component: sine wave over the year
        seasonal = math.sin(2 * math.pi * (day_of_year - 1) / 366) * 50

        # Daily factor
        if 6 <= hour_of_day < 18:
            daily_factor = 1.2
        elif 18 <= hour_of_day < 24:
            daily_factor = 1.0
        else:
            daily_factor = 0.8

        raw = base + seasonal
        val = raw * daily_factor
        val += random.gauss(0, 5)

        # Clip to bounds
        val = max(min_val, min(max_val, val))
        values.append(val)

    return timestamps, values


def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])


def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(mdates.date2num(timestamps), values, linestyle="solid", marker=None)
    plt.title("Hourly Energy Metering")
    plt.xlabel("Timestamp")
    plt.ylabel("Value (kWh)")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()


def main():
    building_id = 110
    min_val = 238.1810427990577
    max_val = 362.9880485248807
    start_year = 2016

    timestamps, values = generate_data(start_year, building_id, min_val, max_val)

    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)


if __name__ == "__main__":
    main()