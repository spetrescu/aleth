import os
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np

ROUND = 8
OUTPUT_DIR = "results/off_the_shelf_llms/quantitative/quantitative_results_incremental_by_no_days"
CSV_FILE = os.path.join(OUTPUT_DIR, f"round_{ROUND}_summary_results.csv")
MEASUREMENTS_PLOT = os.path.join("figure5a.pdf")
TIMING_PLOT = os.path.join("figure5b.pdf")


PALETTE = [
    "#2f171f", "#82c7b7", "#efe3d9", "#E45756",
    "#B279A2", "#72B7B2", "#9D755D", "#BAB0AC",
]
HATCHES = ["///", "\\\\", "xx", "..", "++", "--", "oo", "**"]


def _model_style(models):
    """Returns dict model -> (color, hatch)"""
    styles = {}
    for i, m in enumerate(models):
        styles[m] = (PALETTE[i % len(PALETTE)], HATCHES[i % len(HATCHES)])
    return styles

def load_results(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing CSV file: {csv_path}")

    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            results.append({
                "model": r["model"],
                "requested_days": int(r["requested_days"]),
                "expected_measurements": int(r["expected_measurements"]),
                "actual_measurements": int(r["actual_measurements"]),
                "response_time_s": float(r["response_time_s"]),
            })

    return results

MODEL_DISPLAY_NAMES = {
    "llama3.2": "llama3.2:3b",
    "mistral": "mistral:7b",
}

def plot_measurements(results, path):
    models = sorted({r["model"] for r in results})
    days_sorted = sorted({r["requested_days"] for r in results})
    lookup = {(r["model"], r["requested_days"]): r for r in results}
    styles = _model_style(models)

    fig, ax = plt.subplots(figsize=(10, 2))

    bar_width = 0.8 / len(models)
    x = list(range(len(days_sorted)))

    all_values = []

    for i, model in enumerate(models):
        color, hatch = styles[model]
        x_shifted = [xi + i * bar_width for xi in x]

        for xi, d in zip(x_shifted, days_sorted):
            row = lookup.get((model, d))
            if not row:
                continue

            y_act = row["actual_measurements"]
            expected = d * 24

            all_values.extend([y_act, expected])

            ax.bar(
                xi,
                y_act,
                width=bar_width,
                label=MODEL_DISPLAY_NAMES.get(model, model) if d == days_sorted[0] else None,
                color=color,
                edgecolor="black",
                hatch=hatch,
                alpha=0.9,
            )

            marker_color = "green" if y_act >= expected else "red"
            ax.hlines(
                expected,
                xi - bar_width * 0.42,
                xi + bar_width * 0.42,
                colors=marker_color,
                linewidth=3,
            )

    center_positions = [xi + bar_width * (len(models) - 1) / 2 for xi in x]

    max_ticks = 5
    if len(days_sorted) <= max_ticks:
        tick_idx = list(range(len(days_sorted)))
    else:
        step = (len(days_sorted) - 1) / (max_ticks - 1)
        tick_idx = sorted(set(round(i * step) for i in range(max_ticks)))

    tick_positions = [center_positions[i] for i in tick_idx]
    tick_labels = [f"{days_sorted[i]:02d}" for i in tick_idx]

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=15)

    # Clamp x-axis
    left = center_positions[0] - 0.5
    right = center_positions[-1] + 0.5
    ax.set_xlim(left, right)

    if all_values:
        ymax = max(all_values)

        ymax_plot = ymax + 56 if ymax > 0 else 1

        ymax_plot = np.ceil(ymax_plot)

        ax.set_ylim(0, ymax_plot)
        ax.set_yticks([0, ymax_plot])

    ax.set_xlabel("# requested days", fontsize=15)
    ax.set_ylabel("# Measur.", fontsize=15)
    ax.tick_params(axis="y", labelsize=15)

    ax.set_title("No. actual vs. expected measurements (for # of requested days)", fontsize=15)
    ax.legend(
        title="Model",
        fontsize=15,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
    )
    ax.grid(True, axis="y", alpha=0.2)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_response_times(results, path):
    models = sorted({r["model"] for r in results})
    days_sorted = sorted({r["requested_days"] for r in results})
    lookup = {(r["model"], r["requested_days"]): r for r in results}
    styles = _model_style(models)

    fig, ax = plt.subplots(figsize=(10, 2))

    bar_width = 0.8 / len(models)
    x = list(range(len(days_sorted)))

    all_values = []

    for i, model in enumerate(models):
        color, hatch = styles[model]
        x_shifted = [xi + i * bar_width for xi in x]

        for xi, d in zip(x_shifted, days_sorted):
            row = lookup.get((model, d))
            if not row:
                continue

            y_time = row["response_time_s"]
            all_values.append(y_time)

            ax.bar(
                xi,
                y_time,
                width=bar_width,
                label=MODEL_DISPLAY_NAMES.get(model, model) if d == days_sorted[0] else None,
                color=color,
                edgecolor="black",
                hatch=hatch,
                alpha=0.9,
            )

    center_positions = [xi + bar_width * (len(models) - 1) / 2 for xi in x]

    max_ticks = 5
    if len(days_sorted) <= max_ticks:
        tick_idx = list(range(len(days_sorted)))
    else:
        step = (len(days_sorted) - 1) / (max_ticks - 1)
        tick_idx = sorted(set(round(i * step) for i in range(max_ticks)))

    tick_positions = [center_positions[i] for i in tick_idx]
    tick_labels = [f"{days_sorted[i]:02d}" for i in tick_idx]

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=15)

    left = center_positions[0] - 0.5
    right = center_positions[-1] + 0.5
    ax.set_xlim(left, right)

    if all_values:
        ymax = max(all_values)

        ymax_plot = ymax +4.3 if ymax > 0 else 1

        ax.set_ylim(0, ymax_plot)

        ax.set_yticks([0, ymax_plot])

    ax.set_xlabel("# requested days", fontsize=15)
    ax.set_ylabel("Resp. time (s)", fontsize=15)
    ax.set_title("Response times by model per no. of requested days", fontsize=15)
    ax.tick_params(axis="y", labelsize=15)

    ax.legend(
        title="Model",
        fontsize=15,
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
    )
    ax.grid(True, axis="y", alpha=0.2)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    results = load_results(CSV_FILE)
    plot_measurements(results, MEASUREMENTS_PLOT)
    plot_response_times(results, TIMING_PLOT)
