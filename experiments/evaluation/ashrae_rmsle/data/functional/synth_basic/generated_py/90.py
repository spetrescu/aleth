#!/usr/bin/env python3
import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_timestamps(start_year: int, hours: int):
    start = datetime(start_year, 1, 1, 0, 0)
    return [start + timedelta(hours=i) for i in range(hours)]

def generate_values(num_hours: int, min_val: float, max_val: float, target_total: float):
    base_values = [random.uniform(min_val, max_val) for _ in range(num_hours)]
    sum_base = sum(base_values)
    scale = target_total / sum_base
    return [v * scale for v in base_values]

def main():
    random.seed(42)

    building_id = 90
    start_year = 2016
    hours_per_year = 8760  # 365 days * 24 hours

    # Generate timestamps
    timestamps = generate_timestamps(start_year, hours_per_year)

    # Generate target total energy within the specified range
    min_total = 170.333801583746
    max_total = 247.8908416974116
    target_total = min_total + (max_total - min_total) * random.random()

    # Generate hourly values
    min_hourly = 0.01
    max_hourly = 0.03
    values = generate_values(hours_per_year, min_hourly, max_hourly, target_total)

    # Prepare directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Write CSV
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot data
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plot_path = os.path.join(plot_dir, f"{building_id}.png")
    plt.savefig(plot_path)
    plt.close()

if __name__ == "__main__":
    main()