#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year=2016, building_id=1212,
                         min_total=841.9106417101518,
                         max_total=1217.258135154613):
    random.seed(42)

    # 1 year of hourly data
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = [start_dt + datetime.timedelta(hours=i) for i in range(hours_in_year)]

    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Base consumption pattern: daily and yearly cycles
        daily_cycle = 0.05 * math.sin(2 * math.pi * hour_of_day / 24)
        yearly_cycle = 0.02 * math.sin(2 * math.pi * day_of_year / 365)
        base = 0.1 + daily_cycle + yearly_cycle

        # Random noise
        noise = random.gauss(0, 0.01)
        val = base + noise
        if val < 0:
            val = 0.0
        values.append(val)

    # Scale to target total energy
    current_total = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Consumption for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    building_id = 1212
    timestamps, values = generate_energy_data(building_id=building_id)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()