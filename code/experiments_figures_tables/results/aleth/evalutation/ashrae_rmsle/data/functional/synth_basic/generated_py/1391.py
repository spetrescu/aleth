import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt

MIN_TOTAL = 227.23128787316068
MAX_TOTAL = 328.5650526070966
BUILDING_ID = 1391
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"
DATA_FILE = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
PLOT_FILE = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")

def generate_hourly_data(start_year: int, seed: int = 42):
    random.seed(seed)
    start_dt = datetime.datetime(start_year, 1, 1, 0, 0)
    # 2016 is a leap year, so 366 days
    total_hours = 366 * 24
    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        dt = start_dt + datetime.timedelta(hours=hour_offset)
        timestamps.append(dt)

        day_of_year = dt.timetuple().tm_yday - 1  # 0-based
        hour_of_day = dt.hour

        # Daily factor: higher during day hours
        day_factor = 1.5 if 6 <= hour_of_day < 22 else 0.5

        # Seasonal factor: sinusoidal variation over the year
        seasonal = 1 + 0.2 * math.sin(2 * math.pi * day_of_year / 366)

        base = 0.01  # base consumption in kWh
        noise = random.gauss(0, 0.001)
        value = base * day_factor * seasonal + noise
        if value < 0:
            value = 0.0
        values.append(value)

    # Scale to target total within the specified range
    current_total = sum(values)
    target_total = random.uniform(MIN_TOTAL, MAX_TOTAL)
    scale_factor = target_total / current_total
    values = [v * scale_factor for v in values]

    return timestamps, values

def save_csv(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime("%Y-%m-%dT%H:%M")
            writer.writerow([ts_str, f"{val:.6f}"])

def plot_data(timestamps, values, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Sensor {BUILDING_ID}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

def main():
    timestamps, values = generate_hourly_data(start_year=2016, seed=42)
    save_csv(timestamps, values, DATA_FILE)
    plot_data(timestamps, values, PLOT_FILE)

if __name__ == "__main__":
    main()
</CODE END>