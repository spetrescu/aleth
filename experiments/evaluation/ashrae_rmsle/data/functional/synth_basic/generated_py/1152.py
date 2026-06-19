#!/usr/bin/env python3
import os
import csv
import random
import datetime
import matplotlib.pyplot as plt

def generate_energy_data(building_id: int,
                         start_year: int,
                         total_hours: int,
                         target_total: float,
                         seed: int = 42):
    random.seed(seed)
    # Generate base hourly values with normal distribution
    base_values = []
    for _ in range(total_hours):
        val = random.gauss(0.05, 0.01)
        if val < 0:
            val = 0.0
        base_values.append(val)
    base_sum = sum(base_values)
    scaling_factor = target_total / base_sum
    scaled_values = [v * scaling_factor for v in base_values]
    return scaled_values

def create_timestamps(start: datetime.datetime, total_hours: int):
    return [start + datetime.timedelta(hours=i) for i in range(total_hours)]

def save_csv(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Sensor 1152')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

def main():
    building_id = 1152
    start_year = 2016
    # 2016 is a leap year: 366 days * 24 hours
    total_hours = 366 * 24
    # Target total energy between 351.6995238295556 and 530.47553215808 kWh
    target_total = (351.6995238295556 + 530.47553215808) / 2
    # Generate data
    values = generate_energy_data(building_id, start_year, total_hours, target_total)
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    timestamps = create_timestamps(start_dt, total_hours)
    # Save CSV
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    save_csv(csv_path, timestamps, values)
    # Plot and save PNG
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plot_data(png_path, timestamps, values)

if __name__ == "__main__":
    main()