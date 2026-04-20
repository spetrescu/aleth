import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 5.105624919200002
MAX_VAL = 7.7571077830915
BUILDING_ID = 1069
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"

def generate_data():
    random.seed(42)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    timestamps = []
    values = []
    t = start
    while t.year == 2016:
        hour_of_day = t.hour
        day_of_year = t.timetuple().tm_yday
        # Daily variation
        base_day = (MAX_VAL + MIN_VAL) / 2 + (MAX_VAL - MIN_VAL) / 2 * math.sin(2 * math.pi * hour_of_day / 24)
        # Seasonal variation
        seasonal = (MAX_VAL - MIN_VAL) * 0.1 * math.sin(2 * math.pi * day_of_year / 366)
        # Random noise
        noise = random.gauss(0, 0.05 * (MAX_VAL - MIN_VAL))
        val = base_day + seasonal + noise
        val = max(MIN_VAL, min(MAX_VAL, val))
        timestamps.append(t.strftime("%Y-%m-%dT%H:%M"))
        values.append(val)
        t += datetime.timedelta(hours=1)
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
    dates = [datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.figure(figsize=(12, 6))
    plt.plot_date(dates, values, linestyle='solid', marker=None)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    plt.gcf().autofmt_xdate()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()