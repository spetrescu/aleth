#!/usr/bin/env python3
import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year=2016, building_id=925,
                         min_val=14.174119446410549,
                         max_val=20.6933680828598,
                         seed=42):
    random.seed(seed)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    base = (min_val + max_val) / 2
    amp_daily = (max_val - min_val) / 2
    amp_yearly = 1.0  # seasonal variation amplitude

    timestamps = []
    values = []

    current = datetime(start_year, 1, 1, 0, 0)
    for _ in range(total_hours):
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday

        daily_factor = math.sin(2 * math.pi * hour_of_day / 24)
        yearly_factor = math.sin(2 * math.pi * day_of_year / days_in_year)

        noise = random.uniform(-0.2, 0.2)

        value = base + daily_factor * amp_daily + yearly_factor * amp_yearly + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current)
        values.append(value)

        current += timedelta(hours=1)

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    ax.plot_date(dates, values, '-', linewidth=0.5)
    ax.set_title('Hourly Energy Consumption for Building 925')
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Energy (kWh)')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close(fig)

def main():
    building_id = 925
    timestamps, values = generate_energy_data(building_id=building_id)
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()