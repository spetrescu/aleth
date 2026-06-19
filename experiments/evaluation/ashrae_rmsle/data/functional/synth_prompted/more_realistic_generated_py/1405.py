#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_data(start_year=2016, building_id=1405, seed=42):
    random.seed(seed)
    # Parameters
    base = 0.024          # base hourly consumption (kWh)
    daily_amp = 0.003     # daily variation amplitude
    seasonal_amp = 0.005  # seasonal variation amplitude
    noise_std = 0.001     # noise standard deviation

    # Generate timestamps for one year (non-leap year)
    start = datetime(start_year, 1, 1, 0, 0)
    timestamps = [start + timedelta(hours=i) for i in range(24 * 365)]
    values = []

    for ts in timestamps:
        hour = ts.hour
        day_of_year = ts.timetuple().tm_yday
        daily = daily_amp * math.sin(2 * math.pi * hour / 24)
        seasonal = seasonal_amp * math.sin(2 * math.pi * day_of_year / 365)
        noise = random.gauss(0, noise_std)
        value = base + daily + seasonal + noise
        if value < 0:
            value = 0.0
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Hourly Consumption (kWh)")
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 1405
    timestamps, values = generate_data(building_id=building_id)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()