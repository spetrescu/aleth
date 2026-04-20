import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    end_date = start_date + datetime.timedelta(days=366)  # 2016 is a leap year
    timestamps = []
    values = []

    current = start_date
    while current < end_date:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday

        # Daily cycle: peak at noon
        daily_factor = math.cos((hour_of_day - 12) / 12 * math.pi)
        daily_variation = daily_factor * 4.0  # +/- 4 kWh

        # Seasonal cycle: peak around day 172 (June 21)
        seasonal_factor = math.cos((day_of_year - 172) / 365 * 2 * math.pi)
        seasonal_variation = seasonal_factor * 2.0  # +/- 2 kWh

        noise = random.gauss(0, 0.5)  # small random noise

        base = 24.0
        value = base + daily_variation + seasonal_variation + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(current)
        values.append(value)

        current += datetime.timedelta(hours=1)

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
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.grid(True)

    # Format x-axis with dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.gcf().autofmt_xdate()

    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close()
    return png_path

def main():
    building_id = 605
    min_val = 20.102527055943234
    max_val = 28.43635909298741
    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f'CSV saved to: {csv_path}')
    print(f'Plot saved to: {png_path}')

if __name__ == "__main__":
    main()