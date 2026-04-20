#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year=2016, building_id=1378,
                         min_total=630.9891753936776, max_total=937.7860942007944):
    random.seed(42)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    hours_in_year = 366 * 24
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start_date + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Base pattern: daily sinusoid + seasonal sinusoid
        base = 0.1 + 0.05 * math.sin(2 * math.pi * hour_of_day / 24) \
               + 0.02 * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.uniform(-0.01, 0.01)
        val = max(base + noise, 0.0)
        timestamps.append(ts)
        values.append(val)

    total = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale = target_total / total
    values = [v * scale for v in values]
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
    plt.title(f'Hourly Energy Consumption for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 1378
    timestamps, values = generate_energy_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()