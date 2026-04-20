import csv
import datetime
import math
import os
import random

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def generate_data():
    random.seed(42)

    # Define daily consumption range (kWh)
    daily_min = 83.38888980830478
    daily_max = 123.126893724599

    # Hourly weight pattern (relative usage)
    hour_weights = [
        0.05, 0.05, 0.10, 0.10, 0.15, 0.20, 0.25, 0.30,
        0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.55, 0.50,
        0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10
    ]
    weight_sum = sum(hour_weights)

    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    timestamps = []
    values = []

    # 2016 is a leap year: 366 days
    for day_offset in range(366):
        current_day = start_date + datetime.timedelta(days=day_offset)
        daily_total = random.uniform(daily_min, daily_max)

        for hour in range(24):
            ts = current_day + datetime.timedelta(hours=hour)
            raw = daily_total * hour_weights[hour] / weight_sum
            noise = random.gauss(1, 0.05)
            val = raw * noise
            if val < 0:
                val = 0.0
            timestamps.append(ts)
            values.append(val)

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
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Consumption (kWh)')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis dates
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()


def main():
    timestamps, values = generate_data()
    csv_path = os.path.join('generated_data', '674.csv')
    png_path = os.path.join('generated_plots', '674.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)


if __name__ == "__main__":
    main()