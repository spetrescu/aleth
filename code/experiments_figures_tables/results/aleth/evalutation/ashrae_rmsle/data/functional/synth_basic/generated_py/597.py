#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year=2016, building_id=597,
                  min_val=143.1673818955146, max_val=214.261182232601):
    random.seed(42)
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start_dt + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Base value and variations
        base = 180.0
        daily_amp = 20.0
        seasonal_amp = 5.0
        noise = random.uniform(-5.0, 5.0)

        value = (base
                 + daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
                 + seasonal_amp * math.sin(2 * math.pi * day_of_year / 365)
                 + noise)

        # Clip to specified range
        value = max(min_val, min(max_val, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
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
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 597
    timestamps, values = generate_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()