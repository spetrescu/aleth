import csv
import math
import os
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt


def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)

    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    start_time = datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []

    base = (min_val + max_val) / 2  # midpoint
    daily_amp = 1.0  # amplitude for daily cycle
    seasonal_amp = 0.5  # amplitude for yearly cycle
    noise_std = 0.2  # standard deviation of noise

    for hour_offset in range(total_hours):
        ts = start_time + timedelta(hours=hour_offset)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily variation: sine wave over 24 hours
        daily = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal variation: sine wave over the year
        seasonal = seasonal_amp * math.sin(2 * math.pi * day_of_year / days_in_year)

        # Random noise
        noise = random.gauss(0, noise_std)

        value = base + daily + seasonal + noise
        # Clip to min/max
        value = max(min_val, min(max_val, value))
        value = round(value, 4)

        timestamps.append(ts.strftime('%Y-%m-%dT%H:%M'))
        values.append(value)

    return timestamps, values


def save_csv(timestamps, values, building_id: int):
    output_dir = 'generated_data'
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f'{building_id}.csv')

    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, val])


def plot_data(timestamps, values, building_id: int):
    output_dir = 'generated_plots'
    os.makedirs(output_dir, exist_ok=True)
    png_path = os.path.join(output_dir, f'{building_id}.png')

    # Convert timestamps to datetime objects for plotting
    times = [datetime.strptime(ts, '%Y-%m-%dT%H:%M') for ts in timestamps]

    plt.figure(figsize=(12, 6))
    plt.plot(times, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()


def main():
    building_id = 714
    min_val = 9.239968800803936
    max_val = 13.487966826904179

    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)


if __name__ == "__main__":
    main()