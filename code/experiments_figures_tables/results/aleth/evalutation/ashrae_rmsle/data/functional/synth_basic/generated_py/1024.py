#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt

def generate_data(start_year=2016, building_id=1024,
                  min_val=10.1668082177053, max_val=14.50749961575078,
                  seed=42):
    random.seed(seed)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    end = datetime.datetime(start_year, 12, 31, 23, 0)
    delta = datetime.timedelta(hours=1)

    timestamps = []
    values = []

    current = start
    while current <= end:
        hour = current.hour
        day_of_year = current.timetuple().tm_yday

        # Daily pattern: higher during day, lower at night
        daily_pattern = 1.5 * math.sin(2 * math.pi * hour / 24)

        # Weekly pattern: slight variation over the week
        weekly_pattern = 0.5 * math.sin(2 * math.pi * day_of_year / 7)

        # Base consumption
        base = 12.5

        # Random noise
        noise = random.gauss(0, 0.2)

        value = base + daily_pattern + weekly_pattern + noise
        # Clip to min and max
        value = max(min_val, min(max_val, value))

        timestamps.append(current.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

        current += delta

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    # Convert string timestamps back to datetime for plotting
    times = [datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.plot(times, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 1024
    timestamps, values = generate_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f"CSV saved to: {csv_path}")
    print(f"Plot saved to: {png_path}")

if __name__ == "__main__":
    main()