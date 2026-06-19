import csv
import os
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)

    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    hours_in_year = 366 * 24
    timestamps = []
    values = []

    base = (min_val + max_val) / 2
    amplitude = 0.02  # daily variation amplitude
    for i in range(hours_in_year):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        # Diurnal pattern
        diurnal = amplitude * \
            __import__("math").sin(2 * __import__("math").pi * hour_of_day / 24)
        # Random daily variation
        daily_variation = random.uniform(-0.005, 0.005)
        # Random noise
        noise = random.gauss(0, 0.003)
        val = base + diurnal + daily_variation + noise
        # Clamp to min/max
        val = max(min_val, min(max_val, val))
        timestamps.append(ts)
        values.append(val)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title("Hourly Energy Metering")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 636
    min_val = 0.14810220115103379
    max_val = 0.2212414366651684
    timestamps, values = generate_data(2016, building_id, min_val, max_val)

    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()