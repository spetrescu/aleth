import os
import csv
import math
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_hourly_data(start_year: int, hours: int):
    data = []
    start = datetime(start_year, 1, 1, 0, 0)
    for i in range(hours):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        base = 250.0
        daily_amp = 30.0
        seasonal_amp = 20.0
        noise = random.uniform(-5.0, 5.0)

        value = (
            base
            + daily_amp * math.sin(2 * math.pi * hour_of_day / 24)
            + seasonal_amp * math.sin(2 * math.pi * day_of_year / 365)
            + noise
        )
        # Clip to realistic bounds
        value = max(209.31665955882204, min(307.89105633527214, value))

        data.append((ts.strftime("%Y-%m-%dT%H:%M"), value))
    return data

def save_csv(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        writer.writerows(data)

def plot_data(data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    timestamps = [datetime.strptime(row[0], "%Y-%m-%dT%H:%M") for row in data]
    values = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title("Hourly Energy Metering (kWh)")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    random.seed(42)
    hours_in_year = 24 * 365  # 2016 is a leap year, but we use 365 for simplicity
    data = generate_hourly_data(2016, hours_in_year)

    csv_path = os.path.join("generated_data", "1368.csv")
    png_path = os.path.join("generated_plots", "1368.png")

    save_csv(data, csv_path)
    plot_data(data, png_path)

if __name__ == "__main__":
    main()