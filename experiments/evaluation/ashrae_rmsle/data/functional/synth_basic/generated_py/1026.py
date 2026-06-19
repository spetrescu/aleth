import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

BUILDING_ID = 1026
START_DATE = datetime(2016, 1, 1, 0, 0)
TOTAL_HOURS = 365 * 24  # 2016 is not a leap year
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    timestamps = []
    values = []

    base = 0.015  # base consumption in kWh per hour
    amp_daily = 0.003
    amp_season = 0.002
    noise_std = 0.001

    for i in range(TOTAL_HOURS):
        dt = START_DATE + timedelta(hours=i)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday

        daily_var = amp_daily * math.sin(2 * math.pi * hour_of_day / 24)
        season_var = amp_season * math.sin(2 * math.pi * day_of_year / 365)
        noise = random.gauss(0, noise_std)

        value = base + daily_var + season_var + noise
        if value < 0:
            value = 0.0

        timestamps.append(dt.strftime('%Y-%m-%dT%H:%M'))
        values.append(value)

    # Scale values to have total energy within the specified range
    current_sum = sum(values)
    target_sum = (108.52597586907007 + 161.37987170009123) / 2
    scale_factor = target_sum / current_sum
    values = [v * scale_factor for v in values]

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Consumption for Building {BUILDING_ID}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()