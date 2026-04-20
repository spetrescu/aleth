import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_hourly_data(start_year: int, total_hours: int, seed: int = 42):
    random.seed(seed)
    base = 0.015  # base consumption in kWh
    amplitude = 0.005  # daily variation amplitude
    noise_range = 0.001  # noise amplitude

    start = datetime(start_year, 1, 1, 0, 0)
    timestamps = [start + timedelta(hours=i) for i in range(total_hours)]
    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        daily_pattern = math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.uniform(-noise_range, noise_range)
        value = base + amplitude * daily_pattern + noise
        values.append(value)

    # Scale to target total within specified range
    min_total = 114.91407889746682
    max_total = 164.83710220722972
    current_total = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]
    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 63
    start_year = 2016
    # 2016 is a leap year: 366 days
    total_hours = 366 * 24

    timestamps, values = generate_hourly_data(start_year, total_hours, seed=42)

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()