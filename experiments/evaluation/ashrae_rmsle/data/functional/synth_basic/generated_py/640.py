#!/usr/bin/env python3
import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(building_id: int,
                         start_year: int,
                         csv_path: str,
                         png_path: str) -> None:
    # Create output directories
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    os.makedirs(os.path.dirname(png_path), exist_ok=True)

    # Deterministic random seed
    random.seed(42)

    # Define start and end timestamps
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime.datetime(start_year, 12, 31, 23, 0)
    total_hours = int((end_dt - start_dt).total_seconds() // 3600) + 1

    # Generate timestamps
    timestamps = [start_dt + datetime.timedelta(hours=i) for i in range(total_hours)]

    # Generate hourly values
    values = []
    # Number of days in the year (account for leap year)
    days_in_year = 366 if calendar.isleap(start_year) else 365
    for day in range(days_in_year):
        # Daily total consumption between given bounds
        daily_total = random.uniform(208.93824037957626, 309.21489508781826)

        # Base pattern weights for 24 hours
        hour_weights = [1 + 0.5 * math.sin(2 * math.pi * h / 24) for h in range(24)]

        # Random factors for each hour
        random_factors = [random.random() for _ in range(24)]

        # Weighted random values
        weighted = [rf * w for rf, w in zip(random_factors, hour_weights)]
        sum_weighted = sum(weighted)

        # Scale to match daily total
        day_values = [w * daily_total / sum_weighted for w in weighted]
        values.extend(day_values)

    # Write CSV
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Consumption for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

if __name__ == "__main__":
    import calendar
    building_id = 640
    start_year = 2016
    csv_path = f'generated_data/{building_id}.csv'
    png_path = f'generated_plots/{building_id}.png'
    generate_energy_data(building_id, start_year, csv_path, png_path)
</CODE END>