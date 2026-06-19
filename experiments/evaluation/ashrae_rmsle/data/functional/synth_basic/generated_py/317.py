import csv
import os
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_VAL = 33.25052915858574
MAX_VAL = 48.19524219031458
BUILDING_ID = 317
START_DATE = datetime(2016, 1, 1, 0, 0)
HOURS_PER_YEAR = 365 * 24  # 2016 is not a leap year

def generate_energy_data():
    random.seed(42)
    timestamps = []
    values = []

    base = (MAX_VAL + MIN_VAL) / 2
    amplitude = (MAX_VAL - MIN_VAL) / 2

    for i in range(HOURS_PER_YEAR):
        current_time = START_DATE + timedelta(hours=i)
        hour_of_day = current_time.hour
        day_of_year = current_time.timetuple().tm_yday

        # Daily cycle: peak during midday
        daily_cycle = math.sin(2 * math.pi * hour_of_day / 24)

        # Seasonal cycle: higher consumption in winter (assuming colder months)
        seasonal_cycle = math.sin(2 * math.pi * day_of_year / 365)

        # Combine cycles with equal weight
        combined = 0.5 * daily_cycle + 0.5 * seasonal_cycle

        # Random noise
        noise = random.gauss(0, 0.5)

        value = base + amplitude * combined + noise

        # Clip to min/max
        value = max(MIN_VAL, min(MAX_VAL, value))

        timestamps.append(current_time.strftime("%Y-%m-%dT%H:%M"))
        values.append(value)

    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = f"generated_data/{BUILDING_ID}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.6f}"])

def plot_data(timestamps, values):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    # Convert timestamp strings back to datetime objects for plotting
    times = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.plot(times, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis with date labels
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
    plt.gcf().autofmt_xdate()

    png_path = f"generated_plots/{BUILDING_ID}.png"
    plt.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close()

def main():
    timestamps, values = generate_energy_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()