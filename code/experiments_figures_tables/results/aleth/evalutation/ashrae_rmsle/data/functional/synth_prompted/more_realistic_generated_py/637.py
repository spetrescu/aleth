import os
import csv
import random
import math
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data(start_year: int, building_id: int, min_val: float, max_val: float):
    random.seed(42)

    # Prepare directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # File paths
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    png_path = os.path.join(plot_dir, f"{building_id}.png")

    # Generate timestamps for one year (including leap day if applicable)
    start_dt = datetime(start_year, 1, 1, 0, 0)
    # Determine if leap year
    is_leap = (start_year % 4 == 0 and (start_year % 100 != 0 or start_year % 400 == 0))
    days_in_year = 366 if is_leap else 365
    total_hours = days_in_year * 24

    timestamps = []
    values = []

    for hour_offset in range(total_hours):
        current_dt = start_dt + timedelta(hours=hour_offset)
        timestamps.append(current_dt)

        # Day of year (1-366)
        day_of_year = current_dt.timetuple().tm_yday
        hour_of_day = current_dt.hour

        # Daily cycle: peak during day, trough at night
        daily_amplitude = 0.02
        daily_phase = 2 * math.pi * (hour_of_day - 6) / 24  # peak around 12:00
        daily_component = daily_amplitude * math.sin(daily_phase)

        # Seasonal cycle: higher in summer, lower in winter
        seasonal_amplitude = 0.01
        seasonal_phase = 2 * math.pi * (day_of_year - 80) / 365
        seasonal_component = seasonal_amplitude * math.sin(seasonal_phase)

        # Random noise
        noise = random.uniform(-0.01, 0.01)

        # Base value
        base = (min_val + max_val) / 2

        value = base + daily_component + seasonal_component + noise
        # Clamp to bounds
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
    plt.plot_date(timestamps, values, '-', linewidth=0.5)
    plt.title(f"Energy consumption for building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path, dpi=300)
    plt.close()

if __name__ == "__main__":
    # Parameters
    BUILDING_ID = 637
    START_YEAR = 2016
    MIN_VAL = 0.16076336980320988
    MAX_VAL = 0.23974155500918765

    generate_energy_data(START_YEAR, BUILDING_ID, MIN_VAL, MAX_VAL)
</CODE END>