import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_hourly_data(start_year: int, min_val: float, max_val: float):
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    end = datetime(start_year, 12, 31, 23, 0)
    delta = timedelta(hours=1)
    timestamps = []
    values = []
    current = start
    while current <= end:
        # Daily pattern: higher during day, lower at night
        hour_of_day = current.hour
        daily_factor = math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal pattern: higher in summer, lower in winter
        day_of_year = current.timetuple().tm_yday
        seasonal_factor = math.sin(2 * math.pi * day_of_year / 366)
        # Base value around 24 kWh with variations
        base = 24 + 4 * daily_factor + 2 * seasonal_factor
        # Add random noise
        noise = random.uniform(-0.5, 0.5)
        value = base + noise
        # Clip to specified range
        value = max(min_val, min(max_val, value))
        timestamps.append(current.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)
        current += delta
    return timestamps, values

def save_csv(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # Convert timestamp strings back to datetime for plotting
    times = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot(times, values, linewidth=0.5)
    plt.title("Hourly Energy Metering")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

def main():
    random.seed(42)
    building_id = 605
    min_val = 20.102527055943234
    max_val = 28.43635909298741
    start_year = 2016

    timestamps, values = generate_hourly_data(start_year, min_val, max_val)

    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"

    save_csv(csv_path, timestamps, values)
    plot_data(png_path, timestamps, values)

if __name__ == "__main__":
    main()