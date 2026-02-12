import os
import csv
import matplotlib.pyplot as plt

ROUND = 8
OUTPUT_DIR = "results/off_the_shelf_llms/quantitative/quantitative_results_incremental_by_no_days"
CSV_FILE = os.path.join(OUTPUT_DIR, f"round_{ROUND}_summary_results.csv")
MEASUREMENTS_PLOT = os.path.join("figure5a.png")
TIMING_PLOT = os.path.join("figure5b.png")

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
    if not results:
        print("[warn] No results to plot.")
        return

    models = sorted({r["model"] for r in results})

    days_sorted = sorted({r["requested_days"] for r in results})
    lookup = {(r["model"], r["requested_days"]): r for r in results}
    styles = _model_style(models)

    plt.figure(figsize=(18, 5))
    bar_width = 0.8 / len(models)
    x = list(range(len(days_sorted)))

    for i, model in enumerate(models):
        color, hatch = styles[model]
        x_shifted = [xi + i * bar_width for xi in x]

        for xi, d in zip(x_shifted, days_sorted):
            row = lookup.get((model, d))
            if not row:
                continue

            y_act = row["actual_measurements"]
            expected = d * 24

            plt.bar(
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
            plt.hlines(
                expected,
                xi - bar_width * 0.42,
                xi + bar_width * 0.42,
                colors=marker_color,
                linewidth=3,
            )

    center_positions = [xi + bar_width * (len(models) - 1) / 2 for xi in x]
    plt.xticks(center_positions, days_sorted)

    plt.xlabel("# requested days", fontsize=15)
    plt.ylabel("Actual measurements", fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    plt.title("No. actual vs. expected measurements (for no. of requested days)", fontsize=15)
    plt.legend(title="Model", fontsize=15)
    plt.grid(True, axis="y", alpha=0.2)

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_response_times(results, path):
    if not results:
        print("[warn] No results to plot.")
        return

    models = sorted({r["model"] for r in results})
    days_sorted = sorted({r["requested_days"] for r in results})
    lookup = {(r["model"], r["requested_days"]): r for r in results}
    styles = _model_style(models)

    plt.figure(figsize=(18, 5))
    bar_width = 0.8 / len(models)
    x = list(range(len(days_sorted)))

    for i, model in enumerate(models):
        color, hatch = styles[model]
        x_shifted = [xi + i * bar_width for xi in x]

        for xi, d in zip(x_shifted, days_sorted):
            row = lookup.get((model, d))
            if not row:
                continue

            y_time = row["response_time_s"]

            plt.bar(
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
    plt.xticks(center_positions, days_sorted)

    plt.xlabel("No. requested days", fontsize=15)
    plt.ylabel("Response time (seconds)", fontsize=15)
    plt.title("Response times by model per no. of requested days", fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(title="Model", fontsize=15)
    plt.grid(True, axis="y", alpha=0.2)

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

if __name__ == "__main__":
    results = load_results(CSV_FILE)
    plot_measurements(results, MEASUREMENTS_PLOT)
    plot_response_times(results, TIMING_PLOT)
