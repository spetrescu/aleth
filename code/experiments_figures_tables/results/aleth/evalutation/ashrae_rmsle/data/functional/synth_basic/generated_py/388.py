#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_date, hours, min_val, max_val, seed=0):
    random.seed(seed)
    data = []
    for i in range(hours):
        current_time = start_date + timedelta(hours=i)
        hour_of_day = current_time.hour
        # Daily sinusoidal pattern
        daily_cycle = 0.5 + 0.5 * math.sin(2 * math.pi * (hour_of_day - 6) / 24)
        base = min_val + (max_val - min_val) * daily_cycle
        # Add small Gaussian noise
        noise = random.gauss(0, 0.5)
        value = base + noise
        # Clamp to min/max
        value = max(min_val, min(max_val, value))
        data.append((current_time, value))
    return data

def save_csv(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in data:
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    timestamps, values = zip(*data)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 388
    min_kwh = 35.46100515374695
    max_kwh = 51.38038026469263
    start_date = datetime(2016, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    data = generate_energy_data(start_date, hours_in_year, min_kwh, max_kwh, seed=0)
    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"
    save_csv(csv_path, data)
    plot_data(png_path, data)

if __name__ == "__main__":
    main()