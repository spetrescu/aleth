import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

MIN_TOTAL = 826.1245397064046
MAX_TOTAL = 1206.0368655695304
TARGET_TOTAL = 1000.0  # deterministic target within the range
BUILDING_ID = 785
START_DATE = datetime(2016, 1, 1, 0, 0)

def generate_hourly_pattern():
    """Generate a base hourly consumption pattern for a day."""
    pattern = []
    for hour in range(24):
        # Base pattern: higher during day, lower at night
        base = 0.5 + 1.0 * math.sin(2 * math.pi * (hour - 6) / 24)
        # Add small random noise
        noise = random.uniform(-0.05, 0.05)
        pattern.append(max(0.0, base + noise))
    return pattern

def seasonal_factor(day_of_year):
    """Seasonal factor varying over the year."""
    return 1.0 + 0.2 * math.sin(2 * math.pi * day_of_year / 365)

def main():
    random.seed(42)  # deterministic randomness

    # Prepare directories
    data_dir = 'generated_data'
    plot_dir = 'generated_plots'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Generate data
    base_pattern = generate_hourly_pattern()
    timestamps = []
    values = []

    current = START_DATE
    for day in range(366):  # 2016 is a leap year
        sf = seasonal_factor(day)
        for hour in range(24):
            raw_value = base_pattern[hour] * sf
            # Add small random variation
            raw_value *= random.uniform(0.95, 1.05)
            timestamps.append(current)
            values.append(raw_value)
            current += timedelta(hours=1)

    # Scale to target total
    total = sum(values)
    scale = TARGET_TOTAL / total
    values = [v * scale for v in values]

    # Write CSV
    csv_path = os.path.join(data_dir, f'{BUILDING_ID}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title(f'Hourly Energy Metering for Building {BUILDING_ID}')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    png_path = os.path.join(plot_dir, f'{BUILDING_ID}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    main()