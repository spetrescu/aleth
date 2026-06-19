import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year: int, building_id: int, total_range: tuple):
    random.seed(42)
    # Determine total energy for the year
    total_energy = random.uniform(*total_range)  # kWh

    # Generate hourly timestamps for one year
    start_dt = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = [start_dt + timedelta(hours=i) for i in range(hours_in_year)]

    # Generate raw consumption values with realistic patterns
    raw_values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Base consumption (kWh per hour)
        base = 0.015  # average around 15 Wh

        # Daily variation: higher during day, lower at night
        daily_variation = 0.005 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal variation: higher in winter, lower in summer
        seasonal_variation = 0.003 * math.sin(2 * math.pi * day_of_year / 365)

        # Random noise
        noise = random.gauss(0, 0.001)

        value = base + daily_variation + seasonal_variation + noise
        raw_values.append(value)

    # Scale raw values to match the desired total energy
    raw_sum = sum(raw_values)
    scale_factor = total_energy / raw_sum
    scaled_values = [v * scale_factor for v in raw_values]

    return timestamps, scaled_values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Consumption')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 63
    start_year = 2016
    total_range = (114.91407889746682, 164.83710220722972)

    timestamps, values = generate_energy_data(start_year, building_id, total_range)

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()