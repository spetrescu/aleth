import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id: int, start_year: int = 2016):
    # Set deterministic random seed
    random.seed(42)

    # Define value bounds
    min_val = 0.16076336980320988
    max_val = 0.23974155500918765

    # Base value and amplitude for daily pattern
    base = 0.2
    amplitude = 0.02

    # Determine number of hours in the year (account for leap year)
    start_date = datetime.datetime(start_year, 1, 1, 0, 0)
    end_date = datetime.datetime(start_year + 1, 1, 1, 0, 0)
    total_hours = int((end_date - start_date).total_seconds() // 3600)

    timestamps = []
    values = []

    for i in range(total_hours):
        ts = start_date + datetime.timedelta(hours=i)
        hour_of_day = ts.hour

        # Daily sinusoidal pattern + random noise
        value = base + amplitude * math.sin(2 * math.pi * hour_of_day / 24)
        value += random.uniform(-0.01, 0.01)

        # Clip to bounds
        value = max(min_val, min(max_val, value))

        timestamps.append(ts)
        values.append(value)

    return timestamps, values

def save_csv(building_id: int, timestamps, values):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = f"generated_data/{building_id}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.12f}"])

def plot_and_save(building_id: int, timestamps, values):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True)

    # Format x-axis with dates
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    png_path = f"generated_plots/{building_id}.png"
    plt.savefig(png_path)
    plt.close()

def main():
    building_id = 637
    timestamps, values = generate_data(building_id)
    save_csv(building_id, timestamps, values)
    plot_and_save(building_id, timestamps, values)

if __name__ == "__main__":
    main()