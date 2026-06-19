import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_consumption(start_date, hours, seed=42):
    random.seed(seed)
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(hours)]
    values = []
    for i, ts in enumerate(timestamps):
        hour_of_day = ts.hour
        # Base consumption pattern: 0.01 to 0.02 kWh with daily sinusoidal variation
        base = 0.015 + 0.005 * math.sin(2 * math.pi * hour_of_day / 24)
        # Add small random noise
        noise = random.uniform(-0.001, 0.001)
        val = max(base + noise, 0.0)
        values.append(val)
    # Scale to target total within the specified range
    target_total = random.uniform(101.59339953113249, 149.0005379429272)
    sum_base = sum(values)
    scale_factor = target_total / sum_base if sum_base > 0 else 1.0
    scaled_values = [v * scale_factor for v in values]
    return timestamps, scaled_values

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
    plt.plot_date(timestamps, values, linestyle='solid', marker=None)
    plt.title('Hourly Energy Consumption for Building 944')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 944
    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 8760  # 365 days * 24 hours
    timestamps, values = generate_hourly_consumption(start_date, hours_in_year, seed=42)
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()