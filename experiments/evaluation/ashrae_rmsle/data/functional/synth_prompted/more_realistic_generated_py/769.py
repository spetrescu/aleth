import os
import csv
import datetime
import math
import random
import matplotlib.pyplot as plt

def generate_energy_data():
    random.seed(42)

    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 24 * 365  # 2016 is not a leap year
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(hours_in_year)]

    base = 0.01  # base consumption in kWh per hour
    values = []

    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_factor = 1 + 0.5 * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_factor = 1 + 0.2 * math.sin(2 * math.pi * day_of_year / 365)

        noise = random.uniform(-0.001, 0.001)
        value = base * daily_factor * seasonal_factor + noise
        value = max(value, 0.0)
        values.append(value)

    # Scale to target total energy between the given bounds
    target_total = 70.98632052247326 + (106.12105859199765 - 70.98632052247326) * 0.5
    current_total = sum(values)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('kWh')
    plt.title('Hourly Energy Metering')
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig(filepath, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_energy_data()
    csv_path = os.path.join('generated_data', '769.csv')
    png_path = os.path.join('generated_plots', '769.png')
    save_csv(timestamps, values, csv_path)
    plot_data(timestamps, values, png_path)

if __name__ == "__main__":
    main()