import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int):
    random.seed(42)

    # Define bounds
    min_val = 134.82010567132244
    max_val = 195.3927979635897

    # Base value and amplitudes
    base = (min_val + max_val) / 2
    daily_amp = 20.0
    seasonal_amp = 10.0
    noise_std = 5.0

    # Prepare timestamps
    start = datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    end = datetime(start_year, 12, 31, 23, 0)
    total_hours = int((end - start).total_seconds() // 3600) + 1

    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        ts = start + timedelta(hours=hour_offset)
        timestamps.append(ts)

        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_component = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_component = seasonal_amp * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, noise_std)

        val = base + daily_component + seasonal_component + noise
        val = max(min_val, min(max_val, val))
        values.append(val)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{building_id}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    png_path = f'generated_plots/{building_id}.png'
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 969
    timestamps, values = generate_data(2016, building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()