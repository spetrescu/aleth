import os
import csv
import datetime
import random
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_data():
    random.seed(42)

    start_date = datetime.datetime(2016, 1, 1, 0, 0)
    end_date = datetime.datetime(2016, 12, 31, 23, 0)
    num_hours = 8760
    timestamps = [start_date + datetime.timedelta(hours=i) for i in range(num_hours)]

    values = []

    # Generate data day by day
    for day_offset in range(366):
        day_start = start_date + datetime.timedelta(days=day_offset)
        # Daily total between the specified bounds
        daily_total = random.uniform(68.73440374908921, 102.46854488854834)

        # Create a realistic hourly pattern for the day
        raw_values = []
        random_phase = random.uniform(0, 2 * math.pi)
        for hour in range(24):
            base = 3.5  # average hourly consumption
            amplitude = 0.5  # variation around the base
            val = base + amplitude * math.sin(2 * math.pi * hour / 24 + random_phase)
            noise = random.gauss(0, 0.1)
            raw_val = val + noise
            raw_val = max(raw_val, 0.1)  # ensure positive values
            raw_values.append(raw_val)

        # Scale the day's values to match the target daily total
        sum_raw = sum(raw_values)
        scale_factor = daily_total / sum_raw
        scaled_values = [rv * scale_factor for rv in raw_values]
        values.extend(scaled_values)

    # Save CSV
    os.makedirs('generated_data', exist_ok=True)
    csv_path = os.path.join('generated_data', '515.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'value'])
        for ts, val in zip(timestamps, values):
            writer.writerow([ts.strftime('%Y-%m-%dT%H:%M'), f'{val:.6f}'])

    # Plot the data
    os.makedirs('generated_plots', exist_ok=True)
    plt.figure(figsize=(12, 6))
    dates = mdates.date2num(timestamps)
    plt.plot_date(dates, values, '-', linewidth=0.5)
    plt.title('Hourly Energy Metering (kWh)')
    plt.xlabel('Timestamp')
    plt.ylabel('Value (kWh)')
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    png_path = os.path.join('generated_plots', '515.png')
    plt.savefig(png_path)
    plt.close()

if __name__ == "__main__":
    generate_data()
</CODE END>