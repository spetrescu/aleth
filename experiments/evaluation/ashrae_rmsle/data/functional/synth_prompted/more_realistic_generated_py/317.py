import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 33.25052915858574
MAX_VAL = 48.19524219031458
BUILDING_ID = 317
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_data():
    random.seed(42)
    start = datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start + timedelta(hours=i)
        hour_of_day = ts.hour
        day_of_week = ts.weekday()  # 0=Mon, 6=Sun
        month = ts.month

        # Base consumption
        base = 40.0

        # Daily sinusoidal pattern (amplitude 5 kWh)
        daily_variation = 5.0 * \
            math.sin(2 * math.pi * hour_of_day / 24)

        # Weekly pattern: lower on weekends by 3 kWh
        weekly_variation = -3.0 if day_of_week >= 5 else 0.0

        # Seasonal variation: +2 kWh in winter, -2 kWh in summer
        if month in (12, 1, 2):
            seasonal_variation = 2.0
        elif month in (6, 7, 8):
            seasonal_variation = -2.0
        else:
            seasonal_variation = 0.0

        # Random noise
        noise = random.gauss(0, 1)

        raw_value = (base + daily_variation + weekly_variation +
                     seasonal_variation + noise)

        # Clip to min/max
        value = max(min(raw_value, MAX_VAL), MIN_VAL)

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Consumption for Building {BUILDING_ID}")
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    import math
    main()