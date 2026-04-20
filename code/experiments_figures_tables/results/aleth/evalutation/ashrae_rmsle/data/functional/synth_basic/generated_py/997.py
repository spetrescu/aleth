import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, min_val, max_val, start_year):
    random.seed(0)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year
    days_in_year = 366
    hours_in_year = days_in_year * 24

    mean_val = (min_val + max_val) / 2
    daily_amp = 3.0
    seasonal_amp = 2.0
    noise_std = 0.5

    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start_date + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_component = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_component = seasonal_amp * math.sin(2 * math.pi * day_of_year / days_in_year)
        base = mean_val + daily_component + seasonal_component
        noise = random.gauss(0, noise_std)
        val = base + noise
        val = max(min_val, min(max_val, val))

        timestamps.append(ts)
        values.append(val)

    return timestamps, values

def save_csv(building_id, timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

def plot_data(building_id, timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 997
    min_val = 21.83959409727762
    max_val = 31.76871634529725
    start_year = 2016

    timestamps, values = generate_data(building_id, min_val, max_val, start_year)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)

if __name__ == "__main__":
    main()