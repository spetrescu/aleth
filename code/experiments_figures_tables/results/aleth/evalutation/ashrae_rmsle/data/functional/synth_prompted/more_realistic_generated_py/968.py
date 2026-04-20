#!/usr/bin/env python3
import os
import random
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_energy_data():
    # Constants
    building_id = 968
    min_daily = 162.06821254921218
    max_daily = 236.1781588036529
    start_year = 2016
    start_date = datetime(start_year, 1, 1, 0, 0)
    end_date = datetime(start_year, 12, 31, 23, 0)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Random seed for reproducibility
    random.seed(42)

    # Hourly profile shape (will be normalized)
    hourly_shape = [
        0.02, 0.02, 0.02, 0.02, 0.03, 0.04, 0.06, 0.08,
        0.10, 0.12, 0.15, 0.18, 0.20, 0.18, 0.15, 0.12,
        0.10, 0.08, 0.06, 0.04, 0.03, 0.02, 0.02, 0.02
    ]
    shape_sum = sum(hourly_shape)

    timestamps = []
    values = []

    current_date = start_date
    day_index = 0
    while current_date <= end_date:
        # Compute daily consumption with seasonal sinusoidal pattern
        day_of_year = day_index + 1  # 1-based
        seasonal = (1 + math.sin(2 * math.pi * (day_of_year - 1) / 365)) / 2
        base_daily = min_daily + (max_daily - min_daily) * seasonal
        # Add random noise ±5%
        noise_factor = random.uniform(-0.05, 0.05)
        daily_consumption = base_daily * (1 + noise_factor)
        # Clamp to min/max
        daily_consumption = max(min_daily, min(max_daily, daily_consumption))

        # Generate hourly values for this day
        for hour in range(24):
            hour_timestamp = current_date + timedelta(hours=hour)
            # Base hourly value from shape
            hourly_value = daily_consumption * hourly_shape[hour] / shape_sum
            # Add random noise ±5%
            hourly_noise = random.uniform(-0.05, 0.05)
            hourly_value *= (1 + hourly_noise)
            if hourly_value < 0:
                hourly_value = 0.0
            timestamps.append(hour_timestamp)
            values.append(hourly_value)

        # Move to next day
        current_date += timedelta(days=1)
        day_index += 1

    # Write CSV
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("timestamp,value\n")
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime("%Y-%m-%dT%H:%M")
            f.write(f"{ts_str},{val:.3f}\n")

    # Plotting
    plt.figure(figsize=(12,