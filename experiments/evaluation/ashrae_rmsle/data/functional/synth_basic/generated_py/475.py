import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_dt, hours, base, noise_std, min_total, max_total):
    timestamps = []
    values = []
    for i in range(hours):
        ts = start_dt + datetime.timedelta(hours=i)
        timestamps.append(ts)
        hour_of_day = ts.hour
        # Daily pattern: higher during day, lower at night
        pattern = 1 + 0.5 * math.sin(2 * math.pi * hour_of_day / 24)
        value = base * pattern + random.gauss(0, noise_std)
        value = max(0.0, value)  # ensure non-negative
        values.append(value)
    # Scale to target total
    sum_raw = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale = target_total / sum_raw if sum_raw > 0 else 0
    values = [v * scale for v in values]
    return timestamps, values

def save_csv(file_path, timestamps, values):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(file_path, timestamps, values, building_id):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis with monthly ticks
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

def main():
    random.seed(42)
    building_id = 475
    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    base_consumption = 0.1  # kWh average per hour
    noise_std = 0.02  # kWh
    min_total = 771.3906683265044
    max_total = 1146.746640549507

    timestamps, values = generate_hourly_data(
        start_date, hours_in_year, base_consumption, noise_std, min_total, max_total
    )

    csv_path = f"generated_data/{building_id}.csv"
    png_path = f"generated_plots/{building_id}.png"

    save_csv(csv_path, timestamps, values)
    plot_data(png_path, timestamps, values, building_id)

if __name__ == "__main__":
    main()