import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    total_hours = 365 * 24  # 1 year (non-leap)
    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start + datetime.timedelta(hours=i)
        timestamps.append(ts)

        hour_of_day = ts.hour
        weekday = ts.weekday()  # Monday=0, Sunday=6

        # Base consumption
        base = 40.0

        # Daily pattern: higher during day, lower at night
        daily_variation = 5.0 * math.sin(2 * math.pi * hour_of_day / 24)

        # Weekly pattern: lower on weekends
        weekly_variation = -2.0 if weekday >= 5 else 0.0

        # Random noise
        noise = random.gauss(0, 0.5)

        value = base + daily_variation + weekly_variation + noise
        value = max(min_val, min(max_val, value))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = f'generated_data/{building_id}.csv'
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)
    plt.tight_layout()
    png_path = f'generated_plots/{building_id}.png'
    plt.savefig(png_path, dpi=300)
    plt.close()
    return png_path

def main():
    building_id = 1060
    min_val = 32.90561464535022
    max_val = 47.39962262839086
    timestamps, values = generate_data(2016, building_id, min_val, max_val)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()