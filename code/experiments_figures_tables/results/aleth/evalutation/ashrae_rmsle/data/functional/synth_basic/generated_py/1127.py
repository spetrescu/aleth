import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    # Deterministic random seed
    random.seed(42)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    building_id = 1127
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    png_path = os.path.join(plot_dir, f"{building_id}.png")

    # Generate timestamps for the year 2016 (leap year)
    start = datetime(2016, 1, 1, 0, 0)
    total_hours = 24 * 366  # 366 days in 2016
    timestamps = [start + timedelta(hours=i) for i in range(total_hours)]

    # Generate raw hourly values with a daily pattern
    raw_values = []
    for ts in timestamps:
        hour = ts.hour
        base = random.random()
        # Daily factor: higher during day, lower at night
        factor = 1 + 0.5 * math.sin(2 * math.pi * ((hour - 6) / 24))
        raw_values.append(base * factor)

    raw_sum = sum(raw_values)

    # Target total energy for the year
    target_total = random.uniform(
        100.11372639760795, 144.31276947153228
    )

    # Scale values to match the target total
    scale = target_total / raw_sum
    values = [v * scale for v in raw_values]

    # Write CSV
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot the data
    fig, ax = plt.subplots(figsize=(12, 6))
    dates_num = mdates.date2num(timestamps)
    ax.plot_date(dates_num, values, "-", linewidth=0.5)
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Energy (kWh)")
    ax.set_title(f"Hourly Energy Metering for Building {building_id}")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close(fig)

if __name__ == "__main__":
    main()