import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    # Parameters
    building_id = 530
    min_val = 46.82633434244459
    max_val = 68.09647756224756
    amplitude = (max_val - min_val) / 2.0
    offset = min_val + amplitude
    start_dt = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year

    timestamps = []
    values = []

    for i in range(hours_in_year):
        current_dt = start_dt + datetime.timedelta(hours=i)
        timestamps.append(current_dt)

        hour_of_day = i % 24
        day_of_year = i // 24

        # Daily sinusoidal pattern
        daily = amplitude * math.sin(2 * math.pi * hour_of_day / 24.0)

        # Weekly pattern (smaller amplitude)
        weekly = 0.1 * amplitude * math.sin(2 * math.pi * day_of_year / 7.0)

        # Random noise
        noise = random.gauss(0, 0.5)

        value = offset + daily + weekly + noise
        # Clip to bounds
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val

        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.tight_layout()
    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150)
    plt.close()

def main():
    random.seed(42)
    timestamps, values = generate_data()
    building_id = 530
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()