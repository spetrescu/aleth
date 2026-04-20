#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily pattern: +/-10 kWh around 70 kWh
        daily = 10 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal pattern: +/-5 kWh over the year
        seasonal = 5 * math.sin(2 * math.pi * day_of_year / 365)
        base = 70 + daily + seasonal

        noise = random.gauss(0, 2)
        value = base + noise
        value = max(min_val, min(max_val, value))
        value = round(value, 4)

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), val])

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Energy Metering Data for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 513
    min_val = 60.23385383280047
    max_val = 89.27666629873181
    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()