#!/usr/bin/env python3
import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year=2016, building_id=785,
                         min_total=826.1245397064046,
                         max_total=1206.0368655695304,
                         seed=42):
    random.seed(seed)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Timestamp generation
    start_dt = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = [start_dt + timedelta(hours=i) for i in range(hours_in_year)]

    # Daily factor (relative consumption pattern over 24h)
    daily_factor = [
        0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
        0.10, 0.15, 0.20, 0.25, 0.30, 0.35,
        0.40, 0.45, 0.50, 0.55, 0.60, 0.55,
        0.50, 0.40, 0.30, 0.20, 0.10, 0.05
    ]
    daily_sum = sum(daily_factor)
    daily_norm = [f / daily_sum for f in daily_factor]

    # Weekday factor (lower on weekends)
    weekday_factor = [1.0] * 5 + [0.8, 0.8]  # Mon-Fri, Sat-Sun

    # Monthly factor (seasonal variation)
    month_factor = [1.10, 1.05, 1.00, 0.95, 0.90, 0.85,
                    0.80, 0.85, 0.90, 0.95, 1.00, 1.05]

    # Generate raw values
    raw_values = []
    for ts in timestamps:
        hour = ts.hour
        month = ts.month
        weekday = ts.weekday()  # 0=Mon, 6=Sun

        base = 0.1 * daily_norm[hour]  # base average 0.1 kWh
        factor = weekday_factor[weekday] * month_factor[month - 1]
        noise = random.gauss(0, 0.05)  # 5% noise
        value = base * factor * (1 + noise)
        if value < 0:
            value = 0.0
        raw_values.append(value)

    # Scale to target total
    sum_raw = sum(raw_values)
    target_total = random.uniform(min_total, max_total)
    scale = target_total / sum_raw if sum_raw > 0 else 1.0
    scaled_values = [v * scale for v in raw_values]

    # Write CSV
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, scaled_values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, scaled_values, linewidth=0.5)
    plt.title(f"Hourly Energy Consumption for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    png_path = os.path.join(plot_dir, f"{building_id}.png")
    plt.savefig(png_path, dpi=150)
    plt.close()

def main():
    generate_energy_data()

if __name__ == "__main__":
    main()