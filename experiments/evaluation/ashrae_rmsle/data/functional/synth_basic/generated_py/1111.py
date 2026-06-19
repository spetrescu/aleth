import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year: int, total_hours: int, min_total: float, max_total: float):
    random.seed(42)
    target_total = random.uniform(min_total, max_total)

    # Generate raw random values
    raw_values = [max(random.gauss(0.0065, 0.001), 0.0) for _ in range(total_hours)]
    current_sum = sum(raw_values)
    scale_factor = target_total / current_sum if current_sum != 0 else 0

    # Scale to match target total
    values = [v * scale_factor for v in raw_values]
    return values, target_total

def write_csv(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(file_path: str, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

def main():
    building_id = '1111'
    start_date = datetime(2016, 1, 1, 0, 0)
    total_hours = 365 * 24  # 1 year
    min_total = 46.81394521860747
    max_total = 68.88121218563275

    values, target_total = generate_hourly_data(start_date.year, total_hours, min_total, max_total)
    timestamps = [start_date + timedelta(hours=i) for i in range(total_hours)]

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    write_csv(csv_path, timestamps, values)
    plot_data(png_path, timestamps, values)

if __name__ == "__main__":
    main()