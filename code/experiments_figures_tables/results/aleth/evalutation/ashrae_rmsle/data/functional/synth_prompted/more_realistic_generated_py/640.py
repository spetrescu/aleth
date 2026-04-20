import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)
    min_total = 208.93824037957626
    max_total = 309.21489508781826
    target_total = random.uniform(min_total, max_total)

    start = datetime(2016, 1, 1, 0, 0)
    hours = 366 * 24  # 2016 is a leap year
    timestamps = [start + timedelta(hours=i) for i in range(hours)]

    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday
        base = 0.02
        daily = 0.01 * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal = 0.005 * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.gauss(0, 0.001)
        val = base + daily + seasonal + noise
        values.append(val)

    raw_sum = sum(values)
    scale = target_total / raw_sum
    values = [max(0.0, v * scale) for v in values]

    return timestamps, values, target_total

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{building_id}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = f'generated_plots/{building_id}.png'
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 640
    timestamps, values, target_total = generate_data()
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to {csv_path}')
    print(f'PNG saved to {png_path}')
    print(f'Target total energy: {target_total:.6f} kWh')

if __name__ == "__main__":
    main()