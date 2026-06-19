import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year: int, hours: int, seed: int = 42):
    random.seed(seed)
    base_values = []
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    for i in range(hours):
        current = start + datetime.timedelta(hours=i)
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday
        # Daily pattern: higher during day, lower at night
        daily = 0.05 + 0.05 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal pattern: slight variation over the year
        seasonal = 0.02 * math.sin(2 * math.pi * day_of_year / 365)
        # Random noise
        noise = random.gauss(0, 0.005)
        value = daily + seasonal + noise
        if value < 0:
            value = 0.0
        base_values.append(value)
    return base_values

def scale_values(values, target_total):
    current_total = sum(values)
    if current_total == 0:
        return values
    scale_factor = target_total / current_total
    scaled = [v * scale_factor for v in values]
    return scaled

def write_csv(filepath: str, timestamps, values):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(filepath: str, timestamps, values):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title('Hourly Energy Metering')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    building_id = '1068'
    data_dir = 'generated_data'
    plot_dir = 'generated_plots'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    start_year = 2016
    hours_per_year = 365 * 24  # 8760 hours
    timestamps = []
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    for i in range(hours_per_year):
        ts = start + datetime.timedelta(hours=i)
        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))

    base_values = generate_hourly_data(start_year, hours_per_year, seed=42)

    # Choose a target total within the specified range
    target_total = random.uniform(76.57015951226816, 110.8247923178868)
    values = scale_values(base_values, target_total)

    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    write_csv(csv_path, timestamps, values)

    png_path = os.path.join(plot_dir, f"{building_id}.png")
    plot_data(png_path, timestamps, values)

if __name__ == "__main__":
    main()