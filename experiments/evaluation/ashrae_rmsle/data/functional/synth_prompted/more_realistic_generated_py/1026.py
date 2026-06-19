#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(building_id: int,
                         start_year: int,
                         min_total: float,
                         max_total: float,
                         seed: int = 42):
    random.seed(seed)
    # Determine if start_year is leap year
    is_leap = calendar.isleap(start_year)
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        ts = start_dt + datetime.timedelta(hours=hour_offset)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday  # 1-366

        # Base pattern: daily sinusoid + yearly sinusoid
        daily = 0.05 * math.sin(2 * math.pi * hour_of_day / 24)
        yearly = 0.02 * math.sin(2 * math.pi * day_of_year / days_in_year)
        base = 0.1 + daily + yearly

        # Add small Gaussian noise
        noise = random.gauss(0, 0.01)
        value = base + noise
        if value < 0:
            value = 0.0

        timestamps.append(ts)
        values.append(value)

    # Scale to desired total energy consumption
    current_total = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

    return timestamps, values

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
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 1026
    start_year = 2016
    min_total = 108.52597586907007
    max_total = 161.37987170009123

    timestamps, values = generate_energy_data(building_id, start_year, min_total, max_total)

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    import calendar
    main()