import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data():
    # Parameters
    building_id = 1405
    min_total = 183.280266541122
    max_total = 269.61547891028493
    start_year = 2016
    seed = 42

    # Setup
    random.seed(seed)
    total_hours = 366 * 24  # 2016 is a leap year
    start_time = datetime(start_year, 1, 1, 0, 0)

    # Generate timestamps
    timestamps = [start_time + timedelta(hours=i) for i in range(total_hours)]

    # Generate raw energy values
    raw_values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily cycle: lower at night, higher during day
        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle: higher in winter (approx day 1-90 and 335-366)
        seasonal_cycle = math.sin(2 * math.pi * day_of_year / 366)

        # Base consumption (kWh per hour)
        base = 0.02  # average around 0.02 kWh per hour

        # Amplitude adjustments
        daily_amp = 0.01
        seasonal_amp = 0.01

        # Random noise
        noise = random.uniform(-0.002, 0.002)

        value = base + daily_amp * daily_cycle + seasonal_amp * seasonal_cycle + noise
        raw_values.append(value)

    # Scale to target total within the specified range
    raw_sum = sum(raw_values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / raw_sum
    scaled_values = [v * scale_factor for v in raw_values]

    return timestamps, scaled_values, target_total

def save_csv(timestamps, values, building_id):
    output_dir = "generated_data"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{building_id}.csv")

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id):
    output_dir = "generated_plots"
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, f"{building_id}.png")

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Consumption for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 1405
    timestamps, values, target_total = generate_energy_data()
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)
    print(f"Generated data for building {building_id} with total {target_total:.3f} kWh.")
    print("CSV saved to generated_data/1405.csv")
    print("Plot saved to generated_plots/1405.png")

if __name__ == "__main__":
    main()