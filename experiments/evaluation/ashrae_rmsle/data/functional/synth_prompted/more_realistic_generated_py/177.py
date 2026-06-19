import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data():
    random.seed(42)

    # Parameters
    building_id = 177
    start_year = 2016
    start_date = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year

    # Generate timestamps
    timestamps = [start_date + timedelta(hours=i) for i in range(hours_in_year)]

    # Generate raw values
    raw_values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # Monday=0
        # Base consumption (kWh)
        base = 0.04
        # Daily pattern: higher during day, lower at night
        daily_variation = 0.01 * math.sin(2 * math.pi * hour_of_day / 24)
        # Weekly pattern: slightly lower on weekends
        weekly_variation = 0.005 * math.sin(2 * math.pi * day_of_week / 7)
        # Random noise
        noise = random.gauss(0, 0.002)
        value = base + daily_variation + weekly_variation + noise
        if value < 0:
            value = 0.0
        raw_values.append(value)

    # Scale to target total energy
    target_total = (275.5305868649695 + 398.1825857676519) / 2
    current_total = sum(raw_values)
    scaling_factor = target_total / current_total
    values = [v * scaling_factor for v in raw_values]

    return timestamps, values, building_id

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Consumption for Sensor {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path)
    plt.close()

def main():
    timestamps, values, building_id = generate_energy_data()
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()