#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year=2016, building_id=826, seed=42):
    random.seed(seed)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    timestamps = []
    values = []

    # Parameters for realistic pattern
    base = 61.5          # base consumption in kWh
    daily_amp = 5.0      # daily variation amplitude
    seasonal_amp = 3.0   # seasonal variation amplitude
    noise_amp = 1.0      # random noise amplitude
    min_val = 48.84957680414484
    max_val = 74.1706643676728

    for hour in range(total_hours):
        dt = start_dt + datetime.timedelta(hours=hour)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday

        daily_factor = math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_factor = math.sin(2 * math.pi * day_of_year / days_in_year)
        noise = random.uniform(-noise_amp, noise_amp)

        value = base + daily_amp * daily_factor + seasonal_amp * seasonal_factor + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(dt)
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
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 826
    timestamps, values = generate_data(start_year=2016, building_id=building_id, seed=42)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()