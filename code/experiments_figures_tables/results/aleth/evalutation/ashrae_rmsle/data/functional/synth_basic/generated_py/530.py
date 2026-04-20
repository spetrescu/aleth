#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 46.82633434244459
MAX_VAL = 68.09647756224756
BASE = (MIN_VAL + MAX_VAL) / 2
DAILY_AMPLITUDE = 5.0
SEASONAL_AMPLITUDE = 3.0
NOISE_STD = 0.5
BUILDING_ID = 530
START_DATE = datetime.datetime(2016, 1, 1, 0, 0)
TOTAL_HOURS = 366 * 24  # 2016 is a leap year

def generate_data():
    random.seed(42)
    timestamps = []
    values = []
    for hour_index in range(TOTAL_HOURS):
        current_time = START_DATE + datetime.timedelta(hours=hour_index)
        timestamps.append(current_time)
        day_of_year = hour_index // 24
        hour_of_day = hour_index % 24
        daily_factor = math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_factor = math.sin(2 * math.pi * day_of_year / 365)
        noise = random.gauss(0, NOISE_STD)
        value = BASE + DAILY_AMPLITUDE * daily_factor + SEASONAL_AMPLITUDE * seasonal_factor + noise
        value = max(MIN_VAL, min(MAX_VAL, value))
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{BUILDING_ID}.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {BUILDING_ID}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = f'generated_plots/{BUILDING_ID}.png'
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()