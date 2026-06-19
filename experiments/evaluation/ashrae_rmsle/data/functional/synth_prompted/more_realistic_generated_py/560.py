#!/usr/bin/env python3
import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year, start_month, start_day, hours, seed=42):
    random.seed(seed)
    base_value = 700.0  # base consumption in kWh
    amplitude = 100.0   # daily variation amplitude
    noise_std = 20.0    # standard deviation of noise
    min_val = 582.5378024899746
    max_val = 873.9468486655253

    data = []
    current = datetime(start_year, start_month, start_day, 0, 0)
    for hour in range(hours):
        # Daily sinusoidal variation
        daily_phase = (hour % 24) / 24.0 * 2 * math.pi
        daily_variation = amplitude * math.sin(daily_phase)

        # Seasonal monthly factor
        month = current.month
        if month in (12, 1, 2):
            seasonal_factor = 1.2
        elif month in (6, 7, 8):
            seasonal_factor = 0.9
        else:
            seasonal_factor = 1.0

        # Random noise
        noise = random.gauss(0, noise_std)

        value = base_value + daily_variation
        value *= seasonal_factor
        value += noise

        # Clip to allowed range
        value = max(min_val, min(max_val, value))

        data.append((current.strftime("%Y-%m-%dT%H:%M"), value))
        current += timedelta(hours=1)
    return data

def save_csv(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        writer.writerows(data)

def plot_data(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    timestamps = [datetime.strptime(row[0], "%Y-%m-%dT%H:%M") for row in data]
    values = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    # 2016 is a leap year: 366 days * 24 hours = 8784 hours
    hours_in_year = 366 * 24
    data = generate_hourly_data(2016, 1, 1, hours_in_year, seed=42)

    csv_path = os.path.join('generated_data', '560.csv')
    png_path = os.path.join('generated_plots', '560.png')

    save_csv(data, csv_path)
    plot_data(data, png_path)

if __name__ == "__main__":
    main()