import os
import csv
import random
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Constants
BUILDING_ID = 701
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"
START_DATE = datetime(2016, 1, 1, 0, 0)
END_DATE = datetime(2016, 12, 31, 23, 0)
MIN_DAILY = 39.359701791817386
MAX_DAILY = 57.75300779360088
SEED = 42

# Hourly weight pattern (sum to 1.0)
HOURLY_WEIGHTS = [
    0.05, 0.04, 0.04, 0.04, 0.05, 0.06, 0.07, 0.08,
    0.09, 0.10, 0.12, 0.13, 0.14, 0.13, 0.12, 0.11,
    0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.04
]

def generate_hourly_data():
    random.seed(SEED)
    timestamps = []
    values = []

    current = START_DATE
    while current <= END_DATE:
        timestamps.append(current)
        current += timedelta(hours=1)

    # Group timestamps by day
    day_groups = {}
    for ts in timestamps:
        day = ts.date()
        day_groups.setdefault(day, []).append(ts)

    for day, day_ts in day_groups.items():
        daily_total = random.uniform(MIN_DAILY, MAX_DAILY)
        for i, ts in enumerate(day_ts):
            base = daily_total * HOURLY_WEIGHTS[i]
            noise = random.gauss(0, 0.05 * base)
            value = max(0.0, base + noise)
            values.append(value)

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()