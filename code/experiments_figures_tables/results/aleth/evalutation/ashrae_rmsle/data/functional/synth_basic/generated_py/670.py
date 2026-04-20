import os
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BUILDING_ID = 670
CSV_PATH = f"generated_data/{BUILDING_ID}.csv"
PNG_PATH = f"generated_plots/{BUILDING_ID}.png"
MIN_VAL = 16.407718564460158
MAX_VAL = 24.05585804549171
START_DATE = datetime.datetime(2016, 1, 1, 0, 0)
END_DATE = datetime.datetime(2016, 12, 31, 23, 0)

def generate_data():
    random.seed(42)
    timestamps = []
    values = []
    current = START_DATE
    while current <= END_DATE:
        hour = current.hour
        # Daily sinusoidal pattern centered at 20 kWh with amplitude 3 kWh
        base = 20 + 3 * math.sin(2 * math.pi * hour / 24)
        noise = random.gauss(0, 0.5)
        value = base + noise
        # Clip to specified bounds
        value = max(MIN_VAL, min(MAX_VAL, value))
        timestamps.append(current)
        values.append(value)
        current += datetime.timedelta(hours=1)
    return timestamps, values

def save_csv(timestamps, values):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", encoding="utf-8") as f:
        f.write("timestamp,value\n")
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime("%Y-%m-%dT%H:%M")
            f.write(f"{ts_str},{val:.6f}\n")

def plot_data(timestamps, values):
    os.makedirs(os.path.dirname(PNG_PATH), exist_ok=True)
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.title(f"Hourly Energy Metering for Building {BUILDING_ID}")
    plt.xlabel("Timestamp")
    plt.ylabel("Energy (kWh)")
    plt.grid(True, linestyle='--', alpha=0.5)
    # Format x-axis with dates
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=300)
    plt.close()

def main():
    timestamps, values = generate_data()
    save_csv(timestamps, values)
    plot_data(timestamps, values)

if __name__ == "__main__":
    main()