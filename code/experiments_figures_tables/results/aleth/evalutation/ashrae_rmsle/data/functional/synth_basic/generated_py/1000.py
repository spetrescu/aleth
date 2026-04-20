import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    start_dt = datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []

    for hour in range(total_hours):
        ts = start_dt + timedelta(hours=hour)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday - 1  # zero-indexed

        # Daily cycle: sin wave over 24 hours
        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle: sin wave over year
        seasonal_cycle = math.sin(2 * math.pi * day_of_year / days_in_year)

        # Base value and variations
        base = (min_val + max_val) / 2
        value = base + 10 * daily_cycle + 5 * seasonal_cycle + random.gauss(0, 1)

        # Clamp to min/max
        value = max(min_val, min(max_val, value))

        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    # Convert string timestamps to datetime objects for plotting
    dt_objects = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.plot(dt_objects, values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=150)
    plt.close()

def main():
    random.seed(42)
    building_id = 1000
    min_kwh = 50.052529975278645
    max_kwh = 74.71295290550637
    start_year = 2016

    timestamps, values = generate_data(start_year, building_id, min_kwh, max_kwh)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()