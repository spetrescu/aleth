import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 48.13653442090817
MAX_VAL = 69.13231958480623
BUILDING_ID = 141
START_DATE = datetime(2016, 1, 1, 0, 0)
HOURS_IN_YEAR = 365 * 24  # 2016 is not a leap year

def generate_data():
    random.seed(42)
    timestamps = []
    values = []

    for i in range(HOURS_IN_YEAR):
        current = START_DATE + timedelta(hours=i)
        hour = current.hour
        day_of_year = current.timetuple().tm_yday

        # Daily pattern: higher during day, lower at night
        base = 60.0 if 6 <= hour < 18 else 50.0

        # Seasonal variation: sinusoidal over the year
        seasonal = 5.0 * math.sin(2 * math.pi * day_of_year / 365)

        # Random noise
        noise = random.uniform(-1.0, 1.0)

        value = base + seasonal + noise
        value = max(MIN_VAL, min(MAX_VAL, value))

        timestamps.append(current)
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
    print(f'CSV saved to {csv_path}')

def plot_data(timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {BUILDING_ID}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()

    png_path = f'generated_plots/{BUILDING_ID}.png'
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f'Plot saved to {png_path}')

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()