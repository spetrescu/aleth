import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt

BUILDING_ID = "1368"
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
CSV_PATH = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PNG_PATH = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

MIN_TOTAL = 209.31665955882204
MAX_TOTAL = 307.89105633527214

def generate_hourly_data():
    start = datetime.datetime(2016, 1, 1, 0, 0)
    hours = 365 * 24
    timestamps = [start + datetime.timedelta(hours=i) for i in range(hours)]

    values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        day_of_year = ts.timetuple().tm_yday

        # Base consumption pattern: daily and yearly sinusoidal variations
        base = (
            0.02
            + 0.01 * math.sin(2 * math.pi * hour_of_day / 24)
            + 0.005 * math.sin(2 * math.pi * day_of_year / 365)
        )
        noise = random.gauss(0, 0.002)
        val = base + noise
        if val < 0:
            val = 0.0
        values.append(val)

    total = sum(values)
    target_total = random.uniform(MIN_TOTAL, MAX_TOTAL)
    scale = target_total / total
    values = [v * scale for v in values]

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
    plt.title("Hourly Energy Consumption")
    plt.tight_layout()
    plt.savefig(PNG_PATH)
    plt.close()

def main():
    random.seed(42)
    timestamps, values = generate_hourly_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()