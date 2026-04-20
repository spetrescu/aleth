#!/usr/bin/env python3
import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year, hours, base_value, noise_std):
    data = []
    for _ in range(hours):
        val = base_value + random.gauss(0, noise_std)
        val = max(val, 0.0)
        data.append(val)
    return data

def scale_to_target(data, target_total):
    current_sum = sum(data)
    if current_sum == 0:
        return data
    factor = target_total / current_sum
    return [v * factor for v in data]

def main():
    random.seed(42)

    building_id = 641
    start_date = datetime(start_year := 2016, 1, 1, 0, 0)
    hours_per_year = 365 * 24  # 2016 is not a leap year
    timestamps = [start_date + timedelta(hours=i) for i in range(hours_per_year)]

    # Generate realistic hourly consumption around 0.05 kWh/h
    base_value = 0.05
    noise_std = 0.01
    raw_values = generate_hourly_data(start_year, hours_per_year, base_value, noise_std)

    # Scale to a total between the given bounds
    target_total = random.uniform(341.4948580015958, 510.1096354288321)
    values = scale_to_target(raw_values, target_total)

    # Prepare directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Save CSV
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot_date(timestamps, values, '-', linewidth=0.5)
    ax.set_title(f"Hourly Energy Metering for Building {building_id}")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Energy (kWh)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    plt.tight_layout()

    # Save PNG
    png_path = os.path.join(plot_dir, f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close(fig)

if __name__ == "__main__":
    main()