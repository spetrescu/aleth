import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start_date = datetime(start_year, 1, 1)
    # 2016 is a leap year
    total_hours = 366 * 24
    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        ts = start_date + timedelta(hours=hour_offset)
        hour = ts.hour
        month = ts.month

        # Daily pattern: peak around noon
        daily_pattern = math.sin(2 * math.pi * (hour - 12) / 24)

        # Seasonal pattern: higher in winter, lower in summer
        seasonal_pattern = math.sin(2 * math.pi * (month - 1) / 12)

        base = 38.0
        daily_amp = 5.0
        seasonal_amp = 3.0
        noise = random.gauss(0, 0.5)

        value = base + daily_amp * daily_pattern + seasonal_amp * seasonal_pattern + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = 466
    min_val = 31.23050016015093
    max_val = 44.932407093144626
    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)
    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()