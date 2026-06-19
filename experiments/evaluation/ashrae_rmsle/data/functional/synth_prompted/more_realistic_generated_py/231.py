import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(start_year: int, building_id: int):
    random.seed(42)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # File paths
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    png_path = os.path.join(plot_dir, f"{building_id}.png")

    # Time range: one year hourly
    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year, 12, 31, 23, 0)
    total_hours = int(((end_dt - start_dt).total_seconds() // 3600) + 1)

    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        current_dt = start_dt + timedelta(hours=hour_offset)
        timestamps.append(current_dt)

        # Hour of day and day of year
        hour_of_day = current_dt.hour
        day_of_year = current_dt.timetuple().tm_yday

        # Base consumption and variations
        base = 70.0
        daily_variation = 10.0 * math.sin(2 * math.pi * hour_of_day / 24)
        seasonal_variation = 5.0 * math.sin(2 * math.pi * (day_of_year - 1) / 365)
        noise = random.uniform(-2.0, 2.0)

        value = base + daily_variation + seasonal_variation + noise

        # Clamp to realistic bounds
        min_val = 57.47439463543268
        max_val = 91.79464895777376
        value = max(min_val, min(max_val, value))

        values.append(value)

    # Write CSV
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()

if __name__ == "__main__":
    generate_data(start_year=2016, building_id=231)