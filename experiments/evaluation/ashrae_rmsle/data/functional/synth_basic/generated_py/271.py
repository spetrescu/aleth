import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, low: float, high: float):
    # Determine if leap year
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(start_year + 1, 1, 1)
    delta = timedelta(hours=1)

    timestamps = []
    values = []

    current = start_date
    while current < end_date:
        timestamps.append(current)
        # Generate realistic hourly consumption with daily pattern
        # Base random value
        base = random.uniform(low, high)
        # Add daily sinusoidal variation (peak at 14:00)
        hour = current.hour
        daily_variation = 0.1 * (high - low) * (1 + mdates.sin((hour - 14) * mdates.pi / 12))
        value = base + daily_variation
        # Clamp to [low, high]
        value = max(low, min(high, value))
        values.append(value)
        current += delta

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])
    return csv_path

def plot_data(timestamps, values, building_id: int):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45)

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
    return png_path

def main():
    random.seed(42)
    building_id = 271
    low = 79.16730997325888
    high = 118.86862784050068
    timestamps, values = generate_data(2016, building_id, low, high)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()