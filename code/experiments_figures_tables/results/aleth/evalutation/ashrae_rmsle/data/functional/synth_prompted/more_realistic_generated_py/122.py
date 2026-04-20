import os
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(building_id, start_year, target_sum, hours_per_year):
    random.seed(42)
    base = 0.03  # base hourly consumption in kWh
    daily_amp = 0.01
    seasonal_amp = 0.005
    noise_range = 0.002

    timestamps = []
    values = []

    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    for i in range(hours_per_year):
        current_dt = start_dt + datetime.timedelta(hours=i)
        hour_of_day = i % 24
        day_of_year = i // 24 + 1

        daily_variation = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_variation = seasonal_amp * math.sin(2 * math.pi * day_of_year / 365)
        noise = random.uniform(-noise_range, noise_range)

        value = base + daily_variation + seasonal_variation + noise
        if value < 0:
            value = 0.0

        timestamps.append(current_dt)
        values.append(value)

    # Scale to match target sum
    current_sum = sum(values)
    scale_factor = target_sum / current_sum
    values = [v * scale_factor for v in values]

    return timestamps, values

def save_csv(building_id, timestamps, values):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w') as f:
        f.write('timestamp,value\n')
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime('%Y-%m-%dT%H:%M')
            f.write(f'{ts_str},{val:.6f}\n')

def plot_data(building_id, timestamps, values):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Consumption for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 122
    start_year = 2016
    # 1 year of hourly data: 365 days * 24 hours
    hours_per_year = 365 * 24
    # Target total energy consumption between 225.79135326380492 and 340.01029088598057 kWh
    target_sum = 280.0  # within the specified range

    timestamps, values = generate_energy_data(building_id, start_year, target_sum, hours_per_year)
    save_csv(building_id, timestamps, values)
    plot_data(building_id, timestamps, values)

if __name__ == "__main__":
    main()