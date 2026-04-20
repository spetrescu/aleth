import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    # Parameters
    base = (min_val + max_val) / 2.0
    daily_amp = 15.0
    seasonal_amp = 10.0
    noise_std = 5.0

    # Time range: one year, hourly
    start = datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_variation = daily_amp * math.sin(2 * math.pi * hour_of_day / 24.0)
        seasonal_variation = seasonal_amp * math.sin(2 * math.pi * day_of_year / 365.0)
        noise = random.gauss(0, noise_std)

        value = base + daily_variation + seasonal_variation + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    random.seed(42)
    building_id = 219
    min_val = 150.82548942901101
    max_val = 217.51535916586468

    timestamps, values = generate_data(2016, building_id, min_val, max_val)

    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    png_path = os.path.join('generated_plots', f'{building_id}.png')

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()