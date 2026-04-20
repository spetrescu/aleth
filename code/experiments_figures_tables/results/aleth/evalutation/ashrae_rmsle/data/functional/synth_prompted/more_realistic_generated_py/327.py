import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt

MIN_VALUE = 129.24233834476868
MAX_VALUE = 190.05603896372784
BUILDING_ID = 327
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours_in_year = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []
    for i in range(hours_in_year):
        ts = start + datetime.timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday
        # Daily cycle: +/-20 kWh around 150 kWh
        daily = 20 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal cycle: +/-10 kWh over the year
        seasonal = 10 * math.sin(2 * math.pi * day_of_year / 366)
        base = 150 + daily + seasonal
        noise = random.gauss(0, 2)
        value = base + noise
        # Clip to specified range
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        timestamps.append(ts.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    # Convert timestamps to datetime objects for plotting
    times = [datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 4))
    plt.plot(times, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=150)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()