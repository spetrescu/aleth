import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_hourly_data(start_year: int, total_hours: int):
    timestamps = []
    values = []
    base = 0.5  # base consumption in kWh
    for i in range(total_hours):
        current_time = start_time + timedelta(hours=i)
        hour_of_day = current_time.hour
        day_of_year = current_time.timetuple().tm_yday
        # Daily variation
        daily = 0.3 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal variation
        seasonal = 0.2 * math.sin(2 * math.pi * day_of_year / 366)
        # Random noise
        noise = random.gauss(0, 0.05)
        value = base + daily + seasonal + noise
        if value < 0:
            value = 0.0
        timestamps.append(current_time)
        values.append(value)
    return timestamps, values

def scale_values(values, target_total):
    current_total = sum(values)
    factor = target_total / current_total
    return [v * factor for v in values]

def save_csv(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def save_plot(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering')
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    random.seed(42)
    start_year = 2016
    start_time = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year: 366 days
    total_hours = 366 * 24
    timestamps, values = generate_hourly_data(start_year, total_hours)
    target_total = random.uniform(258.028559740033, 373.0091122189639)
    values = scale_values(values, target_total)
    csv_path = os.path.join('generated_data', '96.csv')
    png_path = os.path.join('generated_plots', '96.png')
    save_csv(csv_path, timestamps, values)
    save_plot(png_path, timestamps, values)