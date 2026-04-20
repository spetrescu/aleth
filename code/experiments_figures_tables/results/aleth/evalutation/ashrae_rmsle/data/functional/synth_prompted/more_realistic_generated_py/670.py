#!/usr/bin/env python3
import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 16.407718564460158
MAX_VAL = 24.05585804549171
BASE_CONSUMPTION = 20.0
DAILY_AMPLITUDE = 3.0
SEASONAL_AMPLITUDE = 2.0
NOISE_STD = 0.5
BUILDING_ID = 670
START_DATE = datetime.datetime(2016, 1, 1, 0, 0)
HOURS_IN_YEAR = 366 * 24  # 2016 is a leap year

def generate_data():
    random.seed(42)
    timestamps = []
    values = []
    for hour in range(HOURS_IN_YEAR):
        current_time = START_DATE + datetime.timedelta(hours=hour)
        hour_of_day = current_time.hour
        hour_of_year = hour

        daily_pattern = DAILY_AMPLITUDE * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_pattern = SEASONAL_AMPLITUDE * math.sin(2 * math.pi * hour_of_year / HOURS_IN_YEAR)
        noise = random.gauss(0, NOISE_STD)

        value = BASE_CONSUMPTION + daily_pattern + seasonal_pattern + noise
        value = max(MIN_VAL, min(MAX_VAL, value))

        timestamps.append(current_time)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{BUILDING_ID}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Consumption for Building {BUILDING_ID}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.grid(True)

    # Format x-axis with dates
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    plt.gca().xaxis.set_major_locator(locator)
    plt.gca().xaxis.set_major_formatter(formatter)

    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{BUILDING_ID}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()