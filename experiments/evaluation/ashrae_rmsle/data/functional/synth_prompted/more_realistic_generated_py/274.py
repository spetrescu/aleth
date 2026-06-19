import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id: int,
                  start_year: int,
                  min_total: float,
                  max_total: float,
                  csv_path: str,
                  png_path: str) -> None:
    random.seed(42)

    # Generate hourly timestamps for one year
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = [start + datetime.timedelta(hours=i) for i in range(hours_in_year)]

    # Generate realistic hourly consumption values
    base = 0.0035          # average kWh per hour
    amplitude = 0.0015     # daily variation
    noise_std = 0.0002     # random noise

    raw_values = []
    for i, ts in enumerate(timestamps):
        hour_of_day = ts.hour
        daily_pattern = amplitude * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.gauss(0, noise_std)
        value = base + daily_pattern + noise
        value = max(value, 0.0)  # ensure non-negative
        raw_values.append(value)

    current_total = sum(raw_values)
    target_total = random.uniform(min_total, max_total)
    scaling_factor = target_total / current_total
    values = [v * scaling_factor for v in raw_values]

    # Ensure directories exist
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)

    # Write CSV
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

    # Plot data
    dates_num = mdates.date2num(timestamps)
    plt.figure(figsize=(12, 6))
    plt.plot_date(dates_num, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Consumption for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    building_id = 274
    start_year = 2016
    min_total = 25.70392138761401
    max_total = 37.15381577759296
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    generate_data(building_id, start_year, min_total, max_total, csv_path, png_path)