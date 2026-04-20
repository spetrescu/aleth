import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    start = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    for h in range(hours_in_year):
        ts = start + timedelta(hours=h)
        hour_of_day = h % 24
        day_of_week = (h // 24) % 7
        day_of_year = (h // 24) % 365

        # Daily cycle: higher consumption during day
        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24) * 5

        # Weekly cycle: slightly lower on weekends
        weekly_cycle = math.sin(2 * math.pi * day_of_week / 7) * 3

        # Seasonal cycle: lower in winter, higher in summer
        seasonal_cycle = math.sin(2 * math.pi * day_of_year / 365) * 2

        # Random noise
        noise = random.gauss(0, 0.5)

        # Base consumption
        base = 81

        value = base + daily_cycle + weekly_cycle + seasonal_cycle + noise

        # Clamp to realistic bounds
        value = max(66.26975946655058, min(96.2161261330028, value))

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

    # Format x-axis with month locator
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close()
    return png_path

def main():
    building_id = 907
    start_year = 2016
    timestamps, values = generate_data(start_year, building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()