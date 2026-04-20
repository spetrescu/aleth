#!/usr/bin/env python3
import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data():
    random.seed(42)

    building_id = 788
    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)

    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(total_hours)]

    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Seasonal variation: sine wave over the year
        seasonal = 1 + 0.2 * math.sin(2 * math.pi * (day_of_year - 1) / 365.25)

        # Daily variation: sine wave over the day
        daily = 1 + 0.3 * math.sin(2 * math.pi * hour_of_day / 24)

        base = 0.03 * seasonal * daily  # base consumption in kWh
        noise = random.gauss(0, 0.005)
        value = max(0.0, base + noise)
        values.append(value)

    total_energy = sum(values)
    target_sum = random.uniform(237.9327205920052, 355.9878017691312)
    scale_factor = target_sum / total_energy
    values = [v * scale_factor for v in values]

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title("Hourly Energy Consumption")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

if __name__ == "__main__":
    generate_energy_data()