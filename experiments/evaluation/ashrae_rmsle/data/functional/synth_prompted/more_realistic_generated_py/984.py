import os
import csv
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def generate_energy_data(start_year=2016, building_id=984,
                         min_daily=42.296675989214194, max_daily=60.94950768470185,
                         seed=42):
    random.seed(seed)
    start_dt = datetime(start_year, 1, 1, 0, 0)
    end_dt = datetime(start_year, 12, 31, 23, 0)
    total_hours = int(((end_dt - start_dt).total_seconds() // 3600) + 1)

    timestamps = []
    values = []

    # Base hourly pattern: 1.5 kWh during night (0-6, 18-24), 2.5 kWh during day (6-18)
    base_pattern = [1.5 if h < 6 or h >= 18 else 2.5 for h in range(24)]

    amplitude = 0.5  # seasonal amplitude in kWh

    current_dt = start_dt
    for hour_index in range(total_hours):
        day_of_year = current_dt.timetuple().tm_yday
        # Seasonal factor for the day
        seasonal = amplitude * math.sin(2 * math.pi * day_of_year / 365)

        # Generate hourly values for the current day if first hour of day
        if hour_index % 24 == 0:
            # Create daily pattern with noise and seasonal
            daily_pattern = []
            for h in range(24):
                noise = random.gauss(0, 0.2)
                val = base_pattern[h] + noise + seasonal
                val = max(val, 0.0)  # avoid negative
                daily_pattern.append(val)
            # Compute sum and scale to target daily total
            current_sum = sum(daily_pattern)
            target_daily = random.uniform(min_daily, max_daily)
            scale = target_daily / current_sum if current_sum > 0 else 1.0
            daily_pattern = [v * scale for v in daily_pattern]
        # Append current hour value
        hour_value = daily_pattern[hour_index % 24]
        timestamps.append(current_dt.strftime("%Y-%m-%dT%H:%M"))
        values.append(hour_value)
        current_dt += timedelta(hours=1)

    return timestamps, values

def save_csv(timestamps, values, building_id):
    os.makedirs("generated_data", exist_ok=True)
    csv_path = f"generated_data/{building_id}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts, f"{val:.4f}"])
    return csv_path

def plot_data(timestamps, values, building_id):
    os.makedirs("generated_plots", exist_ok=True)
    plt.figure(figsize=(12, 6))
    # Convert timestamps to matplotlib date format
    dates = [datetime.strptime(ts, "%Y-%m-%dT%H:%M") for ts in timestamps]
    plt.plot(dates, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.tight_layout()
    png_path = f"generated_plots/{building_id}.png"
    plt.savefig(png_path, dpi=150)
    plt.close()
    return png_path

def main():
    building_id = 984
    timestamps, values = generate_energy_data(building_id=building_id)
    csv_path = save_csv(timestamps, values, building_id)
    png_path = plot_data(timestamps, values, building_id)
    print(f"CSV saved to: {csv_path}")
    print(f"Plot saved to: {png_path}")

if __name__ == "__main__":
    main()