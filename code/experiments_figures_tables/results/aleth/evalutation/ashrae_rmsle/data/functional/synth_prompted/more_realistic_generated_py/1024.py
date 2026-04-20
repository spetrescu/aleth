#!/usr/bin/env python3
import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    # deterministic seed
    random.seed(42)

    # directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # parameters
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 24 * 365  # 2016 is not a leap year
    min_val = 10.1668082177053
    max_val = 14.50749961575078
    base = 12.3  # average consumption

    timestamps = []
    values = []

    for i in range(hours_in_year):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # daily cycle
        daily = 1.0 * math.sin(2 * math.pi * hour_of_day / 24)

        # yearly cycle
        yearly = 1.5 * math.sin(2 * math.pi * (day_of_year - 1) / 365)

        # random noise
        noise = random.gauss(0, 0.2)

        val = base + daily + yearly + noise
        val = max(min_val, min(max_val, val))

        timestamps.append(ts)
        values.append(val)

    # write CSV
    csv_path = os.path.join(data_dir, "1024.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title("Hourly Energy Consumption (kWh)")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join(plot_dir, "1024.png")
    plt.savefig(png_path)
    plt.close()

def main():
    generate_data()

if __name__ == "__main__":
    main()