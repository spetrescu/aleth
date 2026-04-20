#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_timestamps(start_year: int):
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    return [start + datetime.timedelta(hours=i) for i in range(total_hours)]

def generate_consumption_pattern(timestamps):
    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Daily cycle: higher during day
        daily = 0.5 + 0.3 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal cycle: higher in summer
        seasonal = 0.2 * math.sin(2 * math.pi * day_of_year / 366)
        base = daily + seasonal
        # Add random noise
        noise = random.gauss(0, 0.05)
        value = max(base + noise, 0.0)
        values.append(value)
    return values

def scale_to_target_total(values, target_total):
    current_total = sum(values)
    if current_total == 0:
        return values
    factor = target_total / current_total
    return [v * factor for v in values]

def save_csv(timestamps, values, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_and_save(timestamps, values, filepath):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering (kWh)')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    random.seed(42)

    # Directories
    data_dir = 'generated_data'
    plot_dir = 'generated_plots'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Generate timestamps
    timestamps = generate_hourly_timestamps(2016)

    # Generate raw consumption pattern
    raw_values = generate_consumption_pattern(timestamps)

    # Target total energy between given bounds
    target_total = random.uniform(430.84003323375, 647.4830280297615)

    # Scale values to match target total
    values = scale_to_target_total(raw_values, target_total)

    # Save CSV
    csv_path = os.path.join(data_dir, '1220.csv')
    save_csv(timestamps, values, csv_path)

    # Plot and save PNG
    png_path = os.path.join(plot_dir, '1220.png')
    plot_and_save(timestamps, values, png_path)

if __name__ == "__main__":
    main()