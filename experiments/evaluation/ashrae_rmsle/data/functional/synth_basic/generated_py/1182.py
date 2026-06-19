import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, min_val, max_val, start_year):
    random.seed(0)

    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year, 12, 31, 23, 0)

    timestamps = []
    values = []

    current_dt = start_dt
    while current_dt <= end_dt:
        hour = current_dt.hour
        # Daily pattern: sine wave between min and max
        base = (min_val + max_val) / 2 + (max_val - min_val) / 4 * math.sin(2 * math.pi * hour / 24)
        noise = random.gauss(0, 0.2)
        value = base + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current_dt)
        values.append(value)

        current_dt += timedelta(hours=1)

    return timestamps, values

def save_csv(building_id, timestamps, values):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(building_id, timestamps, values):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis with month labels
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.tight_layout()

    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 1182
    min_val = 9.354406038557231
    max_val = 14.046482289758368
    start_year = 2016

    timestamps, values = generate_data(building_id, min_val, max_val, start_year)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)

if __name__ == "__main__":
    main()