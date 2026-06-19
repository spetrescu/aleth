import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data():
    # Configuration
    building_id = 1378
    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"
    start_year = 2016
    min_total = 630.9891753936776
    max_total = 937.7860942007944

    # Ensure output directories exist
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)

    # Set deterministic random seed
    random.seed(42)

    # Determine number of hours in the year (2016 is a leap year)
    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year + 1, 1, 1, 0, 0)
    total_hours = int((end_dt - start_dt).total_seconds() // 3600)

    # Generate timestamps
    timestamps = [start_dt + timedelta(hours=i) for i in range(total_hours)]

    # Generate base pattern (daily + seasonal)
    base_values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily pattern: higher during day, lower at night
        daily = 1 + 0.5 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal pattern: higher in winter, lower in summer
        seasonal = 1 + 0.3 * math.sin(2 * math.pi * day_of_year / 366)

        base = daily * seasonal
        base_values.append(base)

    # Normalize base pattern to sum to 1
    sum_base = sum(base_values)
    base_values = [v / sum_base for v in base_values]

    # Add random noise and ensure positivity
    noisy_values = []
    for v in base_values:
        noise = random.gauss(0, 0.05)  # 5% standard deviation
        val = v * (1 + noise)
        if val < 0:
            val = 0.0
        noisy_values.append(val)

    # Scale to target total energy consumption
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / sum(noisy_values)
    final_values = [v * scale_factor for v in noisy_values]

    # Write CSV
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, final_values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot data
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, final_values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig(png_path)
    plt.close()

if __name__ == "__main__":
    generate_energy_data()