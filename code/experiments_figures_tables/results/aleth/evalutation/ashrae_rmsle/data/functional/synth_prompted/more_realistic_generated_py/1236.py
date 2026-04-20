#!/usr/bin/env python3
import os
import csv
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(building_id, start_year, min_total, max_total):
    random.seed(42)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    days_in_year = 366
    hours_in_day = 24
    total_hours = days_in_year * hours_in_day

    # Pattern for hourly distribution (sums to 1.0)
    pattern = [0.02] * 6 + [0.04] * 6 + [0.06] * 6 + [0.04] * 6

    timestamps = []
    values = []

    for day in range(days_in_year):
        daily_total = random.uniform(min_total, max_total)

        hourly_factors = [random.uniform(0.9, 1.1) for _ in range(hours_in_day)]
        hourly_raw = [daily_total * pattern[i] * hourly_factors[i] for i in range(hours_in_day)]
        sum_raw = sum(hourly_raw)
        scale = daily_total / sum_raw if sum_raw != 0 else 0
        hourly_values = [x * scale for x in hourly_raw]

        # Add small Gaussian noise
        for i in range(hours_in_day):
            noise = random.gauss(0, 0.05)
            val = hourly_values[i] + noise
            if val < 0:
                val = 0.0
            hourly_values[i] = val

        for hour in range(hours_in_day):
            timestamp = start_date + datetime.timedelta(days=day, hours=hour)
            timestamps.append(timestamp)
            values.append(hourly_values[hour])

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.3f}'])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering for Building 1236')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    building_id = 1236
    start_year = 2016
    min_total = 57.571574357537166
    max_total = 88.0880104022142

    timestamps, values = generate_energy_data(building_id, start_year, min_total, max_total)

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == '__main__':
    main()
</CODE END>