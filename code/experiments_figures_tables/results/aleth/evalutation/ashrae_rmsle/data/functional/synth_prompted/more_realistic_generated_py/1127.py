#!/usr/bin/env python3
import os
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year, building_id, total_min, total_max):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    end = datetime.datetime(start_year, 12, 31, 23, 0)
    delta = datetime.timedelta(hours=1)

    timestamps = []
    values = []

    # Generate base consumption pattern
    while start <= end:
        hour = start.hour
        day_of_year = start.timetuple().tm_yday

        # Daily pattern: higher during day (6-18)
        day_factor = 1.0 if 6 <= hour <= 18 else 0.5

        # Seasonal factor: higher in winter, lower in summer
        seasonal = 1.0 + 0.2 * math.sin(2 * math.pi * (day_of_year - 80) / 365)

        # Base consumption in kWh per hour
        base = 0.02 + 0.03 * day_factor + 0.01 * seasonal

        # Add random noise
        noise = random.uniform(-0.005, 0.005)
        value = max(base + noise, 0.0)

        timestamps.append(start)
        values.append(value)

        start += delta

    # Scale to target total energy
    current_total = sum(values)
    target_total = random.uniform(total_min, total_max)
    scale = target_total / current_total
    values = [v * scale for v in values]

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        f.write('timestamp,value\n')
        for ts, val in zip(timestamps, values):
            f.write(f'{ts.strftime("%Y-%m-%dT%H:%M")},{val:.6f}\n')

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 1127
    start_year = 2016
    total_min = 100.11372639760795
    total_max = 144.31276947153228

    timestamps, values = generate_hourly_data(start_year, building_id, total_min, total_max)

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    import math
    main()