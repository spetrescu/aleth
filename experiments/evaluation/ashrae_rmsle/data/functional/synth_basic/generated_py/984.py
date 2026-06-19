#!/usr/bin/env python3
import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, min_total: float, max_total: float):
    random.seed(42)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    hours_in_year = days_in_year * 24

    # Generate timestamps
    start_dt = datetime(start_year, 1, 1, 0, 0)
    timestamps = [start_dt + timedelta(hours=i) for i in range(hours_in_year)]

    # Target total energy
    target_total = random.uniform(min_total, max_total)

    # Generate random proportions
    random_vals = [random.random() for _ in range(hours_in_year)]
    sum_random = sum(random_vals)
    values = [rv / sum_random * target_total for rv in random_vals]

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id: int):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 984
    min_total = 42.296675989214194
    max_total = 60.94950768470185
    timestamps, values = generate_data(2016, building_id, min_total, max_total)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()