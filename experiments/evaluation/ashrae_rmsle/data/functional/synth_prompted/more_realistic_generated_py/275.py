import csv
import math
import os
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    range_val = max_val - min_val
    amplitude_daily = range_val * 0.3
    amplitude_seasonal = range_val * 0.1
    noise_scale = range_val * 0.05

    for hour_offset in range(total_hours):
        dt = start_dt + datetime.timedelta(hours=hour_offset)
        hour_of_day = dt.hour
        day_of_year = dt.timetuple().tm_yday

        daily_cycle = amplitude_daily * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_cycle = amplitude_seasonal * math.sin(2 * math.pi * day_of_year / 366)
        noise = random.uniform(-noise_scale, noise_scale)

        value = (min_val + max_val) / 2 + daily_cycle + seasonal_cycle + noise
        value = max(min_val, min(max_val, value))

        timestamps.append(dt)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values, building_id: int):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = os.path.join("generated_data", f"{building_id}.csv")
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for dt, val in zip(timestamps, values):
            writer.writerow([dt.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values, building_id: int):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join("generated_plots", f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 275
    min_val = 118.28946765487859
    max_val = 175.30554980163924
    timestamps, values = generate_energy_data(2016, building_id, min_val, max_val)
    save_csv(timestamps, values, building_id)
    plot_data(timestamps, values, building_id)

if __name__ == "__main__":
    main()