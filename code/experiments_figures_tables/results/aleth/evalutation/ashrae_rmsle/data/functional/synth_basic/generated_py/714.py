#!/usr/bin/env python3
import os
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)
    min_val = 9.239968800803936
    max_val = 13.487966826904179
    base = (min_val + max_val) / 2  # 11.363967813854058

    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_per_day = 24
    days_per_year = 365
    total_hours = days_per_year * hours_per_day  # 8760

    timestamps = []
    datetime_list = []
    values = []

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
        datetime_list.append(ts)

        # Daily variation: sine wave over 24 hours
        daily_variation = 1.0 * math.sin(2 * math.pi * (i % hours_per_day) / hours_per_day)

        # Seasonal variation: sine wave over the year
        seasonal_variation = 1.0 * math.sin(2 * math.pi * i / total_hours)

        # Random noise
        noise = random.gauss(0, 0.2)

        value = base + daily_variation + seasonal_variation + noise
        value = max(min_val, min(max_val, value))
        values.append(value)

    return timestamps, datetime_list, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        f.write('timestamp,value\n')
        for ts, val in zip(timestamps, values):
            f.write(f'{ts},{val:.6f}\n')

def plot_data(datetime_list, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(datetime_list, values, '-', linewidth=0.5)
    plt.title('Energy Metering for Building 714')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, datetime_list, values = generate_data()
    csv_path = os.path.join('generated_data', '714.csv')
    png_path = os.path.join('generated_plots', '714.png')
    save_csv(timestamps, values, csv_path)
    plot_data(datetime_list, values, png_path)

if __name__ == "__main__":
    main()