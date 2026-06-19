import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year: int, building_id: int, min_daily: float, max_daily: float):
    random.seed(42)

    start_date = datetime(start_year, 1, 1)
    end_date = datetime(start_year, 12, 31, 23, 0)
    total_hours = int((end_date - start_date).total_seconds() // 3600) + 1

    timestamps = []
    values = []

    # Precompute hour factors for daily pattern
    hour_factors = [1 + 0.5 * math.sin((hour - 6) / 24 * 2 * math.pi) for hour in range(24)]
    sum_hour_factors = sum(hour_factors)

    for hour_index in range(total_hours):
        current_time = start_date + timedelta(hours=hour_index)
        timestamps.append(current_time)

        day_of_year = (current_time.date() - start_date.date()).days + 1
        seasonal_factor = 1 + 0.1 * math.sin((day_of_year - 80) / 365 * 2 * math.pi)

        # Daily total with seasonal variation
        daily_total = random.uniform(min_daily, max_daily) * seasonal_factor

        # Hourly value before noise
        hour_factor = hour_factors[current_time.hour]
        base_value = daily_total * hour_factor / sum_hour_factors

        # Add random noise ±5%
        noisy_value = base_value * random.uniform(0.95, 1.05)

        # Ensure non-negative
        noisy_value = max(noisy_value, 0.0)

        values.append(noisy_value)

    return timestamps, values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.4f}'])

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Consumption for Building 999')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 999
    min_daily = 102.94474202149634
    max_daily = 149.78647831842613
    start_year = 2016

    timestamps, values = generate_hourly_data(start_year, building_id, min_daily, max_daily)

    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'

    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()
</CODE END>