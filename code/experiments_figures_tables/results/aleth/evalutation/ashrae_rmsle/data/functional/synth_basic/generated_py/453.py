import os
import csv
import random
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id: int,
                  min_total: float,
                  max_total: float,
                  seed: int = 42):
    random.seed(seed)

    # Directories
    data_dir = "generated_data"
    plot_dir = "generated_plots"
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # File paths
    csv_path = os.path.join(data_dir, f"{building_id}.csv")
    png_path = os.path.join(plot_dir, f"{building_id}.png")

    # Generate timestamps for 2016 (leap year)
    start = datetime.datetime(2016, 1, 1, 0, 0)
    total_hours = 366 * 24  # 2016 is a leap year
    timestamps = [start + datetime.timedelta(hours=i) for i in range(total_hours)]

    # Generate raw values
    raw_values = []
    for ts in timestamps:
        hour_of_day = ts.hour
        base = 0.003  # base consumption in kWh
        daily_variation = 0.001 * math.sin(2 * math.pi * hour_of_day / 24)
        noise = random.gauss(0, 0.0002)
        value = base + daily_variation + noise
        if value < 0:
            value = 0.0
        raw_values.append(value)

    # Scale to target total
    target_total = random.uniform(min_total, max_total)
    sum_raw = sum(raw_values)
    scaling_factor = target_total / sum_raw if sum_raw != 0 else 0
    scaled_values = [v * scaling_factor for v in raw_values]

    # Write CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, scaled_values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

    # Plot
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot_date(timestamps, scaled_values, linestyle='-', marker=None)
    ax.set_title(f"Energy Metering for Building {building_id}")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Energy (kWh)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close(fig)

if __name__ == "__main__":
    BUILDING_ID = 453
    MIN_TOTAL = 21.771437495978113
    MAX_TOTAL = 31.535128828917774
    generate_data(BUILDING_ID, MIN_TOTAL, MAX_TOTAL)