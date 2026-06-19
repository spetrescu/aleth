import csv
import os
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year: int, hours: int, seed: int = 0):
    random.seed(seed)
    base_values = []
    for hour in range(hours):
        hour_of_day = hour % 24
        # Daily sinusoidal pattern
        daily_pattern = 0.01 * (1 + 0.5 * (1 + math.sin(2 * math.pi * hour_of_day / 24)))
        # Random noise
        noise = random.uniform(-0.005, 0.005)
        value = 0.03 + daily_pattern + noise
        base_values.append(value)

    # Scale to desired total energy between min_total and max_total
    min_total = 244.71375699963068
    max_total = 362.9613544854476
    target_total = random.uniform(min_total, max_total)
    current_total = sum(base_values)
    scale_factor = target_total / current_total
    scaled_values = [v * scale_factor for v in base_values]
    return scaled_values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title("Hourly Energy Metering")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    import math
    start_date = datetime(2016, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = [(start_date + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M") for i in range(hours_in_year)]
    values = generate_hourly_data(start_year=2016, hours=hours_in_year, seed=0)

    csv_path = os.path.join("generated_data", "1086.csv")
    png_path = os.path.join("generated_plots", "1086.png")

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()