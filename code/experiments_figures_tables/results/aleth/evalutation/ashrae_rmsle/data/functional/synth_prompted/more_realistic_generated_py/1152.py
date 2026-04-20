import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)

    # Generate timestamps for the entire year 2016 (leap year)
    start = datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = [start + timedelta(hours=i) for i in range(total_hours)]

    # Generate realistic hourly consumption values
    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday  # 1-366

        # Base consumption pattern
        base = 0.1  # kWh
        daily_amp = 0.15
        seasonal_amp = 0.05

        daily = base + daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal = seasonal_amp * math.sin(2 * math.pi * (day_of_year - 1) / 366)
        noise = random.uniform(-0.02, 0.02)

        value = daily + seasonal + noise
        if value < 0:
            value = 0.0
        values.append(value)

    # Scale values to meet total energy between given bounds
    total = sum(values)
    target_total = random.uniform(351.6995238295556, 530.47553215808)
    scale_factor = target_total / total
    values = [v * scale_factor for v in values]

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    dates = mdates.date2num(timestamps)

    plt.figure(figsize=(12, 6))
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title('Hourly Energy Consumption for Sensor 1152')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.grid(True)

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '1152.csv')
    png_path = os.path.join('generated_plots', '1152.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()