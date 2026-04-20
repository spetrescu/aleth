import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VALUE = 40.46044203476045
MAX_VALUE = 60.840926235492525
BUILDING_ID = 682
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_hourly_data(start_year: int):
    random.seed(42)
    data = []
    start = datetime(start_year, 1, 1, 0, 0)
    end = datetime(start_year, 12, 31, 23, 0)
    current = start
    while current <= end:
        hour_of_day = current.hour
        day_of_year = current.timetuple().tm_yday
        # Daily cycle: higher during day, lower at night
        daily_cycle = 5 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal cycle: higher in winter (assuming heating)
        seasonal_cycle = 5 * math.sin(2 * math.pi * day_of_year / 366)
        base = 50 + daily_cycle + seasonal_cycle
        noise = random.uniform(-1, 1)
        value = base + noise
        # Clamp to min/max
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        timestamp_str = current.strftime("%Y-%m-%dT%H:%M")
        data.append((timestamp_str, round(value, 3)))
        current += timedelta(hours=1)
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
    plt.ylabel("Power (kW)")
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()

def main():
    data = generate_hourly_data(2016)
    save_csv(data, CSV_PATH)
    plot_data(data, PNG_PATH)

if __name__ == "__main__":
    main()