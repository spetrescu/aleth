import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Constants
BUILDING_ID = 1296
MIN_VALUE = 12.728388395912841
MAX_VALUE = 18.6549444635869
BASE_VALUE = 15.0  # average consumption
DAILY_AMPLITUDE = 3.0  # variation amplitude
NOISE_RANGE = 0.5  # noise +/- range
START_DATE = datetime.datetime(2016, 1, 1, 0, 0)
TOTAL_HOURS = 365 * 24  # one year

CSV_DIR = "generated_data"
PNG_DIR = "generated_plots"
CSV_PATH = os.path.join(CSV_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PNG_DIR, f"{BUILDING_ID}.png")

def generate_data():
    random.seed(42)
    timestamps = []
    values = []
    for hour in range(TOTAL_HOURS):
        ts = START_DATE + datetime.timedelta(hours=hour)
        hour_of_day = ts.hour
        # Daily sinusoidal pattern
        daily_variation = DAILY_AMPLITUDE * math.sin(2 * math.pi * hour_of_day / 24)
        # Random noise
        noise = random.uniform(-NOISE_RANGE, NOISE_RANGE)
        value = BASE_VALUE + daily_variation + noise
        # Clip to min/max
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        timestamps.append(ts)
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(CSV_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PNG_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()