import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = "."

FEATHER_PATH = os.path.join(DATA_DIR, "../../data/electrical_metering_bgdp2/data_files/building_metadata.feather")
CSV_PATH = os.path.join(DATA_DIR, "../../data/electrical_metering_bgdp2/data_files/building_metadata.csv")


def load_building_metadata():
    if os.path.exists(FEATHER_PATH):
        print("Loading building_metadata.feather")
        return pd.read_feather(FEATHER_PATH)
    elif os.path.exists(CSV_PATH):
        print("Loading building_metadata.csv")
        return pd.read_csv(CSV_PATH)
    else:
        raise FileNotFoundError("Could not find building_metadata.feather or building_metadata.csv")


def main():
    df = load_building_metadata()

    counts = (
        df["primary_use"]
        .value_counts()
        .sort_values(ascending=False)
    )

    top_two = ["#29757F", "#55A868"]

    base_palette = [       
        "#515475",
        "#6f75a6",
        "#8f97db",
        "#a6a2e3",
        "#b9a6e1",
        "#ccabdf",
        "#ddafdd",
        "#ebb5db",
        "#e8beda",
        "#e6c7d9",
    ]

    extra_palette = [
        "#d6c2e8",
        "#cbb9e3",
        "#f0c2d8",
        "#f3cedf",
    ]

    rest_palette = base_palette + extra_palette
    colors = []
    if len(counts) >= 1:
        colors.append(top_two[0])
    if len(counts) >= 2:
        colors.append(top_two[1])

    remaining = len(counts) - len(colors)
    if remaining > 0:
        colors.extend((rest_palette * ((remaining // len(rest_palette)) + 1))[:remaining])

    tick_labels = []
    for i, label in enumerate(counts.index):
        if i < 2:
            tick_labels.append(label[:9])
        else:
            tick_labels.append(label[:8]+".")

    y = range(len(counts))

    plt.figure(figsize=(4, 4))
    bars = plt.barh(
        y,
        counts.values,
        color=colors,
        edgecolor="black",
        linewidth=0.6,
    )

    plt.title("Number of buildings by primary use")
    plt.xlabel("Number of buildings")
    plt.yticks(
        ticks=y,
        labels=tick_labels,
        va="center"
    )
    plt.gca().invert_yaxis()

    plt.tight_layout()

    plt.savefig("figure2a.png", dpi=150)
    print("Saved plot to figure2a.png")


if __name__ == "__main__":
    main()
