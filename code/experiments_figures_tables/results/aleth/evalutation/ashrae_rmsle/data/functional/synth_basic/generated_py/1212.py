import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_hourly_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year: 366 days * 24 hours = 8784 hours
    total_hours = 366 * 24
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(total_hours)]

    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Daily variation: peak around noon
        daily_factor = 0.5 * (1 + math.sin(2 * math.pi * (hour_of_day - 6) / 24))
        # Seasonal variation: peak around day 80 (approx. March 21)
        seasonal_factor = 0.5 * (1 + math.sin(2 * math.pi * (day_of_year - 80) / 365))

        base = 0.3 + 0.3 * daily_factor + 0.1 * seasonal_factor
        noise = random.uniform(-0.05, 0.05)
        value = base + noise
        if value < 0:
            value = 0.0
        values.append(value)

    # Scale to target total energy between given bounds
    min_total = 841.9106417101518
    max_total = 1217.258135154613
    target_total = random.uniform(min_total, max_total)
    current_total = sum(values)
    scale_factor = target_total / current_total
    scaled_values = [v * scale_factor for v in values]

    return timestamps, scaled_values, target_total

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
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering for Building 1212')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 1212
    start_year = 2016
    timestamps, values, target_total = generate_hourly_data(start_year, building_id)
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)
    print(f'Generated CSV: {csv_path}')
    print(f'Generated PNG: {png_path}')
    print(f'Target total energy: {target_total:.3f} kWh')

if __name__ == "__main__":
    main()