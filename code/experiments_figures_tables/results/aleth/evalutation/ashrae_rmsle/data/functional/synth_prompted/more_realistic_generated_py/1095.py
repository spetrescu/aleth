import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 51.946693965093075
MAX_VAL = 76.32933375297397
BUILDING_ID = 1095
START_DATE = datetime(2016, 1, 1, 0, 0)
TOTAL_HOURS = 366 * 24  # 2016 is a leap year

def generate_data():
    random.seed(42)
    data = []
    for hour_offset in range(TOTAL_HOURS):
        ts = START_DATE + timedelta(hours=hour_offset)
        hour = ts.hour
        month = ts.month

        # Daily cycle: peak at noon
        daily_factor = 0.5 * (1 + math.sin(2 * math.pi * (hour - 12) / 24))

        # Seasonal adjustment: higher in winter, lower in summer
        if month in (12, 1, 2):
            seasonal_variation = 1
        elif month in (6, 7, 8):
            seasonal_variation = -1
        else:
            seasonal_variation = 0
        seasonal_factor = 1 + 0.2 * seasonal_variation

        # Base value
        base = MIN_VAL + (MAX_VAL - MIN_VAL) * daily_factor * seasonal_factor

        # Add small random noise
        noise = random.gauss(0, 0.5)
        value = base + noise

        # Clamp to allowed range
        value = max(MIN_VAL, min(MAX_VAL, value))

        data.append((ts.strftime("%Y-%m-%dT%H:%M"), value))
    return data

def save_csv(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        writer.writerows(data)

def plot_data(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    timestamps = [datetime.strptime(row[0], "%Y-%m-%dT%H:%M") for row in data]
    values = [row[1] for row in data]

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    plt.gcf().autofmt_xdate()

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def main():
    data = generate_data()
    csv_path = f"generated_data/{BUILDING_ID}.csv"
    png_path = f"generated_plots/{BUILDING_ID}.png"
    save_csv(data, csv_path)
    plot_data(data, png_path)

if __name__ == "__main__":
    main()