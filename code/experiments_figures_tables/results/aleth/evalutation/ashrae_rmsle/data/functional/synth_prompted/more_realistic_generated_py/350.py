import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)

    # Parameters
    building_id = 350
    min_total = 118.18391464136994
    max_total = 176.32977188297235
    daily_amp = 0.2          # kWh variation over a day
    seasonal_amp = 0.1       # kWh variation over a year
    base_offset = 0.1        # base consumption to avoid negatives
    noise_std = 0.02         # standard deviation of noise

    # Generate timestamps for 2016 (leap year)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24
    timestamps = [start + datetime.timedelta(hours=i) for i in range(hours_in_year)]

    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday - 1  # 0-365

        daily_cycle = 0.5 * (math.sin(2 * math.pi * hour_of_day / 24) + 1)
        seasonal_cycle = 0.5 * (math.sin(2 * math.pi * day_of_year / 366) + 1)

        base = base_offset + daily_cycle * daily_amp + seasonal_cycle * seasonal_amp
        noise = random.gauss(0, noise_std)
        value = base + noise
        if value < 0:
            value = 0.0
        values.append(value)

    # Scale to target total energy
    current_total = sum(values)
    target_total = random.uniform(min_total, max_total)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

    return timestamps, values, building_id

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150)
    plt.close()

def main():
    timestamps, values, building_id = generate_data()
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()