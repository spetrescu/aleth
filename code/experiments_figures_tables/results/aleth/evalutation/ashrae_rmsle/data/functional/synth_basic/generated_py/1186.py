#!/usr/bin/env python3
import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    timestamps = []
    values = []

    base_time = datetime(start_year, 1, 1, 0, 0)
    for hour_index in range(total_hours):
        current_time = base_time + timedelta(hours=hour_index)
        hour_of_day = current_time.hour
        day_of_year = current_time.timetuple().tm_yday

        # Daily cycle: higher during day, lower at night
        daily_cycle = 20 * (0.5 * (1 + math.sin(2 * math.pi * hour_of_day / 24 - math.pi / 2)))
        # Seasonal cycle: higher in summer, lower in winter
        seasonal_cycle = 10 * math.sin(2 * math.pi * day_of_year / 365 - math.pi / 2)

        # Base value around middle of range
        base_value = (min_val + max_val) / 2

        # Random noise
        noise = random.uniform(-5, 5)

        value = base_value + daily_cycle + seasonal_cycle + noise
        # Clamp to min and max
        value = max(min_val, min(max_val, value))

        timestamps.append(current_time)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plot_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    return plot_path

def main():
    random.seed(42)
    import math  # Imported here to avoid unused import warning if not used elsewhere
    building_id = 1186
    min_val = 133.98870778211247
    max_val = 199.75409982677175
    start_year = 2016

    timestamps, values = generate_data(start_year, building_id, min_val, max_val)
    csv_path = save_csv(timestamps, values, building_id)
    plot_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {plot_path}')

if __name__ == "__main__":
    main()