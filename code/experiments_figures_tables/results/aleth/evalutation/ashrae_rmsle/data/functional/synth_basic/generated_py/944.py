#!/usr/bin/env python3
import os
import csv
import random
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data(building_id, start_year, min_total, max_total):
    random.seed(42)
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    hours = 365 * 24  # 1 year
    timestamps = [start + datetime.timedelta(hours=i) for i in range(hours)]
    total = random.uniform(min_total, max_total)
    raw = [random.random() for _ in range(hours)]
    raw_sum = sum(raw)
    values = [r / raw_sum * total for r in raw]
    return timestamps, values

def save_csv(building_id, timestamps, values, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"{building_id}.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "value"])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime("%Y-%m-%dT%H:%M"), f"{val:.6f}"])

def plot_data(building_id, timestamps, values, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.title(f"Hourly Energy Metering for Building {building_id}")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join(output_dir, f"{building_id}.png")
    plt.savefig(png_path, dpi=300)
    plt.close()

def main():
    building_id = 944
    start_year = 2016
    min_total = 101.59339953113249
    max_total = 149.0005379429272
    timestamps, values = generate_data(building_id, start_year, min_total, max_total)
    save_csv(building_id, timestamps, values, "generated_data")
    plot_data(building_id, timestamps, values, "generated_plots")

if __name__ == "__main__":
    main()