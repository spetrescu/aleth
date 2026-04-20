import os
import random
import math
import datetime
import matplotlib.pyplot as plt

def generate_hourly_timestamps(start_year: int, hours: int):
    timestamps = []
    start = datetime.datetime(start_year, 1, 1, 0, 0)
    for i in range(hours):
        timestamps.append(start + datetime.timedelta(hours=i))
    return timestamps

def generate_energy_values(total_energy: float, hours: int):
    # Generate exponential random numbers for Dirichlet-like distribution
    exp_vals = [-math.log(random.random()) for _ in range(hours)]
    sum_exp = sum(exp_vals)
    weights = [x / sum_exp for x in exp_vals]

    # Apply a daily pattern factor (higher during day, lower at night)
    pattern_factors = []
    for h in range(hours):
        hour_of_day = h % 24
        # Pattern: 1 + 0.5 * sin(2π * hour/24)
        factor = 1 + 0.5 * math.sin(2 * math.pi * hour_of_day / 24)
        pattern_factors.append(factor)

    # Adjust weights by pattern factors
    adjusted = [w * f for w, f in zip(weights, pattern_factors)]
    sum_adjusted = sum(adjusted)
    final_weights = [x / sum_adjusted for x in adjusted]

    # Compute hourly values
    values = [w * total_energy for w in final_weights]
    return values

def write_csv(file_path: str, timestamps, values):
    with open(file_path, 'w') as f:
        f.write('timestamp,value\n')
        for ts, val in zip(timestamps, values):
            ts_str = ts.strftime('%Y-%m-%dT%H:%M')
            f.write(f'{ts_str},{val:.6f}\n')

def plot_and_save(timestamps, values, file_path: str):
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, values, linewidth=0.5)
    plt.xlabel('Timestamp')
    plt.ylabel('Energy (kWh)')
    plt.title('Hourly Energy Metering')
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

def main():
    random.seed(42)

    # Parameters
    min_total = 102.94474202149634
    max_total = 149.78647831842613
    building_id = 999
    hours_in_year = 365 * 24  # 2016 is not a leap year

    # Generate total energy within the specified range
    total_energy = random.uniform(min_total, max_total)

    # Generate timestamps
    timestamps = generate_hourly_timestamps(2016, hours_in_year)

    # Generate energy values
    values = generate_energy_values(total_energy, hours_in_year)

    # Prepare directories
    data_dir = 'generated_data'
    plot_dir = 'generated_plots'
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    # Write CSV
    csv_path = os.path.join(data_dir, f'{building_id}.csv')
    write_csv(csv_path, timestamps, values)

    # Plot and save PNG
    png_path = os.path.join(plot_dir, f'{building_id}.png')
    plot_and_save(timestamps, values, png_path)

if __name__ == '__main__':
    main()