import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DATA_DIR = "."

FILES = {
    "building_meta_feather": os.path.join(DATA_DIR, "../../data/electrical_metering_bgdp2/data_files/building_metadata.feather"),
    "building_meta_csv": os.path.join(DATA_DIR, "../../data/electrical_metering_bgdp2/data_files/building_metadata.csv"),
    "train_feather": os.path.join(DATA_DIR, "../../data/electrical_metering_bgdp2/data_files/train.feather"),
    "train_csv": os.path.join(DATA_DIR, "../../data/electrical_metering_bgdp2/data_files/train.csv"),
}


def load_df(feather_path, csv_path, name):
    if os.path.exists(feather_path):
        print(f"Loading {name} from feather")
        return pd.read_feather(feather_path)
    elif os.path.exists(csv_path):
        print(f"Loading {name} from csv")
        return pd.read_csv(csv_path)
    else:
        raise FileNotFoundError(f"Could not find {name} file.")


def main():
    building_meta = load_df(
        FILES["building_meta_feather"],
        FILES["building_meta_csv"],
        "building_metadata",
    )

    train = load_df(
        FILES["train_feather"],
        FILES["train_csv"],
        "train",
    )

    Education_meta = building_meta[building_meta["primary_use"] == "Education"].copy()
    Education_building_ids = set(Education_meta["building_id"])

    print(f"Total Education buildings: {Education_meta.shape[0]}")

    Education_train = train[train["building_id"].isin(Education_building_ids)].copy()

    buildings_with_electric = set(
        Education_train.loc[Education_train["meter"] == 0, "building_id"]
    )

    buildings_without_electric = Education_building_ids - buildings_with_electric

    electric_count = len(buildings_with_electric)
    non_electric_count = len(buildings_without_electric)

    print(f"Education buildings WITH electric (meter=0): {electric_count}")
    print(f"Education buildings WITHOUT electric: {non_electric_count}")

    plt.figure(figsize=(5, 5))
    plt.hist(
        Education_meta["square_feet"].dropna(),
        bins=50,
        color="#29757F",
        edgecolor="black",
        linewidth=0.5,
    )
    plt.title("Square feet distribution (Education buildings)", fontsize=13)
    plt.xlabel("Square feet", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.ylabel("Number of buildings", fontsize=16)
    ax = plt.gca()
    ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=4))
    ax.xaxis.set_minor_locator(mticker.NullLocator())

    plt.tight_layout()
    plt.savefig("figure2b.png", dpi=150)
    plt.close()

if __name__ == "__main__":
    main()
