import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)

    # Define time range: 1 year starting from Jan 1 of start_year
    start_dt = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24  # 8784 hours

    timestamps = []
    raw_values = []

    for hour_offset in range(total_hours):
        ts = start_dt + timedelta(hours=hour_offset)
        timestamps.append(ts)

        # Daily pattern: sinusoidal variation over 24 hours
        hour_of_day = ts.hour
        daily_pattern = 0.01 + 0.005 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal pattern: sinusoidal variation over the year
        day_of_year = ts.timetuple().tm_yday
        seasonal_pattern = 0.002 * math.sin(2 * math.pi * day_of_year / 366)

        # Random noise
        noise = random.uniform(-0.0005, 0.0005)

        raw_value = daily_pattern + seasonal_pattern + noise
        raw_value = max(raw_value, 0.0)  # Ensure non-negative
        raw_values.append(raw_value)

    # Scale to target total energy between given bounds
    target_total = random.uniform(57.571574357537166, 88.0880104022142)
    raw_total = sum(raw_values)
    scale_factor = target_total / raw_total

    scaled_values = [v * scale_factor for v in raw_values]

    return timestamps, scaled_values, target_total

def save_csv(timestamps, values, building_id: int, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{building_id}.csv")
    with open(csv_path, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id: int, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Consumption for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis with monthly ticks
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join(output_dir, f"{building_id}.png")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close()

def main():
    building_id = 1236
    start_year = 2016
    seed = 42

    timestamps, values, target_total = generate_energy_data(start_year, building_id, seed)

    csv_output_dir = "generated_data"
    png_output_dir = "generated_plots"

    save_csv(timestamps, values, building_id, csv_output_dir)
    plot_data(timestamps, values, building_id, png_output_dir)

    print(f"Generated data for building {building_id} with total energy {target_total:.6f} kWh.")
    print(f"CSV saved to {os.path.join(csv_output_dir, f'{building_id}.csv')}")
    print(f"Plot saved to {os.path.join(png_output_dir, f'{building_id}.png')}")

if __name__ == "__main__":
    main()