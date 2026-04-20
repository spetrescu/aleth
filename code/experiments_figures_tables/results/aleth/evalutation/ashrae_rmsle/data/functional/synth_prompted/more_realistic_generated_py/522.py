import os
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_data():
    # Parameters
    building_id = 522
    min_val = 17.39358412431408
    max_val = 25.222707621942995
    base = (min_val + max_val) / 2.0
    daily_amp = 2.0          # daily variation amplitude
    seasonal_amp = 1.0       # seasonal variation amplitude
    noise_std = 0.5          # standard deviation of noise

    # Time range: 2016-01-01 00:00 to 2016-12-31 23:00 (leap year)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = [start + datetime.timedelta(hours=i) for i in range(hours_in_year)]

    # Generate values
    values = []
    for i in range(hours_in_year):
        daily = daily_amp * math.sin(2 * math.pi * i / 24.0)
        seasonal = seasonal_amp * math.sin(2 * math.pi * i / (365 * 24.0))
        noise = random.gauss(0, noise_std)
        val = base + daily + seasonal + noise
        val = max(min_val, min(max_val, val))
        values.append(val)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', f'{building_id}.csv')
    with open(csv_path, 'w') as f:
        f.write('timestamp,value\n')
        for ts, val in zip(timestamps, values):
            f.write(f'{ts.strftime("%Y-%m-%dT%H:%M")},{val:.6f}\n')

def plot_data(timestamps, values, building_id):
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot_date(timestamps, values, '-', linewidth=0.5)
    plt.title(f'Hourly Energy Metering for Building {building_id}')
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.tight_layout()
    png_path = os.path.join('generated_plots', f'{building_id}.png')
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    random.seed(42)
    building_id = 522
    timestamps, values = generate_data()
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()