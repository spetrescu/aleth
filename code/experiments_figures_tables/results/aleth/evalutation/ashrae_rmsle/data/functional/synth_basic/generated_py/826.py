import os
import csv
import math
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VALUE = 48.84957680414484
MAX_VALUE = 74.1706643676728
BASE_VALUE = (MIN_VALUE + MAX_VALUE) / 2
DAILY_AMPLITUDE = 5.0
HOURLY_AMPLITUDE = 10.0
NOISE_RANGE = 2.0
BUILDING_ID = 826
START_DATE = datetime(2016, 1, 1, 0, 0)
TOTAL_HOURS = 366 * 24  # 2016 is a leap year

def generate_data():
    random.seed(42)
    timestamps = []
    values = []
    for i in range(TOTAL_HOURS):
        current_time = START_DATE + timedelta(hours=i)
        hour_of_day = current_time.hour
        day_of_year = current_time.timetuple().tm_yday
        daily_variation = math.sin(2 * math.pi * day_of_year / 366)
        hourly_variation = math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.uniform(-NOISE_RANGE, NOISE_RANGE)
        value = (BASE_VALUE +
                 DAILY_AMPLITUDE * daily_variation +
                 HOURLY_AMPLITUDE * hourly_variation +
                 noise)
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        timestamps.append(current_time)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{BUILDING_ID}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {BUILDING_ID}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = f'generated_plots/{BUILDING_ID}.png'
    plt.savefig(png_path)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()