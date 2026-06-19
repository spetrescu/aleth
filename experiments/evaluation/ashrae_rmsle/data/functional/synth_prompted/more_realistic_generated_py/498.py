import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(building_id: int, start_year: int = 2016,
                         min_val: float = 22.41569420643628,
                         max_val: float = 32.54442686179401,
                         seed: int = 42):
    random.seed(seed)
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily pattern: sine wave over 24 hours
        daily = 3.0 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal pattern: sine wave over the year
        seasonal = 2.0 * math.sin(2 * math.pi * day_of_year / 366)

        # Base consumption
        base = 27.5

        # Random noise
        noise = random.gauss(0, 0.5)

        value = base + daily + seasonal + noise
        # Clamp to specified range
        value = max(min_val, min(max_val, value))

        timestamps.append(ts.strftime('%Y-%m-%dT%H:%M'))
        values.append(value)

    return timestamps, values

def save_csv(building_id: int, timestamps, values, output_dir: str = 'generated_data'):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f'{val:.6f}'])

def plot_data(building_id: int, timestamps, values, output_dir: str = 'generated_plots'):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(12, 6))
    # Convert string timestamps back to datetime for plotting
    dt_timestamps = [datetime.strptime(ts, '%Y-%m-%dT%H:%M') for ts in timestamps]
    plt.plot(dt_timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join(output_dir, f'{building_id}.png')
    plt.savefig(png_path, dpi=150)
    plt.close()

def main():
    building_id = 498
    timestamps, values = generate_energy_data(building_id)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)

if __name__ == "__main__":
    main()