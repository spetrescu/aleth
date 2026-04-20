#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year=2016, building_id=475,
                         min_total=771.3906683265044, max_total=1146.746640549507,
                         seed=42):
    random.seed(seed)
    # Create datetime list for one year hourly
    start_dt = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = [start_dt + timedelta(hours=i) for i in range(hours_in_year)]

    # Generate raw hourly consumption values
    raw_values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily pattern: sin wave between 0.2 and 0.8
        daily_factor = 0.5 + 0.3 * math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal pattern: small variation +/-5%
        seasonal_factor = 0.05 * math.sin(2 * math.pi * (day_of_year - 1) / 365)

        base = 1.0  # base kWh per hour
        value = base * daily_factor * (1 + seasonal_factor)

        # Add small random noise
        noise = random.gauss(0, 0.05)
        value += noise

        # Ensure positive
        value = max(value, 0.05)
        raw_values.append(value)

    # Scale to target total energy consumption
    total_raw = sum(raw_values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / total_raw
    scaled_values = [v * scale_factor for v in raw_values]

    # Final check: ensure no negative values
    scaled_values = [max(v, 0.05) for v in scaled_values]

    return timestamps, scaled_values, target_total

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{building_id}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Energy Metering Data for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    png_path = f'generated_plots/{building_id}.png'
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 475
    timestamps, values, target_total = generate_energy_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')
    print(f'Target total energy: {target_total:.2f} kWh')

if __name__ == "__main__":
    main()