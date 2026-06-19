import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int, seed: int = 42):
    random.seed(seed)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    hours_in_year = 365 * 24  # 2016 is not a leap year
    timestamps = []
    values = []

    base = 0.02  # kWh per hour
    daily_amp = 0.005
    seasonal_amp = 0.003
    noise_std = 0.001

    for i in range(hours_in_year):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        daily_variation = daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_variation = seasonal_amp * math.sin(2 * math.pi * day_of_year / 365)
        noise = random.gauss(0, noise_std)

        value = base + daily_variation + seasonal_variation + noise
        if value < 0:
            value = 0.001
        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id: int):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title(f"Hourly Energy Consumption for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.grid(True)

    # Format x-axis with month locator
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 597
    timestamps, values = generate_data(start_year=2016, building_id=building_id)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()