#!/usr/bin/env python3
import os
import csv
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)

    min_total = 57.47439463543268
    max_total = 91.79464895777376
    target_total = random.uniform(min_total, max_total)

    n_hours = 365 * 24  # 2016 is a leap year? 2016 is a leap year, so 366 days
    # Adjust for leap year
    if datetime.date(2016, 2, 29).year == 2016:
        n_hours = 366 * 24

    raw_values = [max(0.1, random.gauss(1, 0.2)) for _ in range(n_hours)]
    sum_raw = sum(raw_values)
    values = [v / sum_raw * target_total for v in raw_values]

    start = datetime.datetime(2016, 1, 1, 0, 0)
    timestamps = [start + datetime.timedelta(hours=i) for i in range(n_hours)]
    formatted_timestamps = [ts.strftime('%Y-%m-%dT%H:%M') for ts in timestamps]

    return formatted_timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f'{val:.6f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    dates = [datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M') for ts in timestamps]
    ax.plot(dates, values, linewidth=0.5)
    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Energy (kWh)')
    ax.set_title('Hourly Energy Metering for Sensor 231')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close(fig)

def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '231.csv')
    png_path = os.path.join('generated_plots', '231.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()