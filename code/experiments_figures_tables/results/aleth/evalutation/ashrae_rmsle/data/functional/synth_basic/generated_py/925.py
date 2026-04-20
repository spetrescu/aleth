import os
import csv
import random
import datetime
import math
import matplotlib.pyplot as plt

def generate_data(start_date, hours, min_val, max_val):
    data = []
    base = (min_val + max_val) / 2
    amplitude = (max_val - min_val) / 4
    for i in range(hours):
        timestamp = start_date + datetime.timedelta(hours=i)
        hour_of_day = timestamp.hour
        day_of_year = timestamp.timetuple().tm_yday
        daily_pattern = math.sin(2 * math.pi * hour_of_day / 24)
        yearly_pattern = math.sin(2 * math.pi * day_of_year / 365)
        value = base + amplitude * daily_pattern + (amplitude / 2) * yearly_pattern
        noise = random.uniform(-0.5, 0.5)
        value += noise
        value = max(min_val, min(max_val, value))
        data.append((timestamp.strftime("%Y-%m-%dT%H:%M"), round(value, 6)))
    return data

def save_csv(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        writer.writerows(data)

def plot_data(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    timestamps = [datetime.datetime.strptime(row[0], "%Y-%m-%dT%H:%M") for row in data]
    values = [row[1] for row in data]
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering')
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

def main():
    random.seed(42)
    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    hours = 24 * 365
    min_val = 14.174119446410549
    max_val = 20.6933680828598
    data = generate_data(start_date, hours, min_val, max_val)
    csv_path = os.path.join('generated_data', '925.csv')
    png_path = os.path.join('generated_plots', '925.png')
    save_csv(data, csv_path)
    plot_data(data, png_path)

if __name__ == "__main__":
    main()