import os
import csv
import math
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Constants
BUILDING_ID = 421
START_DATE = datetime.datetime(2016, 1, 1, 0, 0)
HOURS_PER_YEAR = 365 * 24  # 8760
MIN_VALUE = 23.557394837295437
MAX_VALUE = 35.59328748179138

# Parameters for realistic data generation
BASE_MEAN = 29.5
SEASONAL_AMPLITUDE = 3.0
DAILY_AMPLITUDE = 2.0
NOISE_STD = 0.5

# Directories
DATA_DIR = "generated_data"
PLOT_DIR = "generated_plots"

def generate_timestamps():
    """Generate hourly timestamps for one year starting from START_DATE."""
    timestamps = []
    for i in range(HOURS_PER_YEAR):
        ts = START_DATE + datetime.timedelta(hours=i)
        timestamps.append(ts)
    return timestamps

def generate_values(timestamps):
    """Generate realistic energy values for each timestamp."""
    values = []
    for ts in timestamps:
        day_of_year = ts.timetuple().tm_yday
        hour_of_day = ts.hour

        # Seasonal component (annual cycle)
        seasonal = SEASONAL_AMPLITUDE * math.sin(
            2 * math.pi * (day_of_year - 1) / 365
        )

        # Daily component (peak around 14:00)
        daily = DAILY_AMPLITUDE * math.sin(
            2 * math.pi * (hour_of_day - 14) / 24
        )

        # Random noise
        noise = random.gauss(0, NOISE_STD)

        value = BASE_MEAN + seasonal + daily + noise
        # Clip to specified bounds
        value = max(MIN_VALUE, min(MAX_VALUE, value))
        values.append(value)
    return values

def save_csv(timestamps, values):
    """Save timestamps and values to CSV."""
    os.makedirs(DATA_DIR, exist_ok=True)
    csv_path = os.path.join(DATA_DIR, f"{BUILDING_ID}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(timestamps, values):
    """Plot the energy data and save as PNG."""
    os.makedirs(PLOT_DIR, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True, linestyle="--", alpha=0.5)

    # Format x-axis with month ticks
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.xticks(rotation=45)

    plt.tight_layout()
    png_path = os.path.join(PLOT_DIR, f"{BUILDING_ID}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    random.seed(42)  # Deterministic output
    timestamps = generate_timestamps()
    values = generate_values(timestamps)
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()