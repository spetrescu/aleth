import os
import glob
import argparse
import gc
from datetime import datetime
from typing import Dict, Tuple, List, Optional

import numpy as np
import pandas as pd
import lightgbm as lgb
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

SYNTH_DIRS = {
    "Aleth synthetic": "functional/synth_aleth",
    "Synthetic baseline": "functional/synth_basic",
    "Prompted synthetic": "functional/synth_prompted",
}

def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def get_paths(data_dir: str) -> Dict[str, str]:
    return {
        "train": os.path.join(data_dir, "train.csv"),
        "weather_train": os.path.join(data_dir, "weather_train.csv"),
        "building_feather": os.path.join(data_dir, "building_metadata.feather"),
        "building_csv": os.path.join(data_dir, "building_metadata.csv"),
    }


def load_building_metadata(data_dir: str) -> pd.DataFrame:
    paths = get_paths(data_dir)
    if os.path.exists(paths["building_feather"]):
        return pd.read_feather(paths["building_feather"])
    if os.path.exists(paths["building_csv"]):
        return pd.read_csv(paths["building_csv"])
    raise FileNotFoundError("No building metadata file found.")


def prepare_building_metadata(bm: pd.DataFrame) -> pd.DataFrame:
    bm = bm.copy()
    if "primary_use" in bm.columns:
        bm["primary_use"] = bm["primary_use"].astype("category")
    if "year_built" in bm.columns:
        bm["year_built"] = bm["year_built"].fillna(bm["year_built"].median())
    if "floor_count" in bm.columns:
        bm["floor_count"] = bm["floor_count"].fillna(bm["floor_count"].median())
    return bm


def load_selected_building_ids(path: str, n_buildings: int = 15) -> np.ndarray:
    df = pd.read_csv(path, usecols=["building_id"])
    df = df.drop_duplicates(subset=["building_id"])
    return df["building_id"].astype(int).values[:n_buildings]


def add_time_features(df: pd.DataFrame, ts_col: str = "timestamp") -> pd.DataFrame:
    df = df.copy()
    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
    df = df.dropna(subset=[ts_col])

    df["hour"] = df[ts_col].dt.hour.astype(np.int8)
    df["dayofweek"] = df[ts_col].dt.dayofweek.astype(np.int8)
    df["month"] = df[ts_col].dt.month.astype(np.int8)
    df["day"] = df[ts_col].dt.day.astype(np.int8)
    df["weekofyear"] = df[ts_col].dt.isocalendar().week.astype(np.int16)

    return df


def merge_all(base: pd.DataFrame, weather: pd.DataFrame, building: pd.DataFrame) -> pd.DataFrame:
    base = base.copy()
    building = building.copy()

    if "site_id" not in building.columns:
        raise ValueError("building metadata must contain site_id")

    if "site_id" in base.columns:
        building_no_site = building.drop(columns=["site_id"])
        df = base.merge(building_no_site, on="building_id", how="left")
    else:
        df = base.merge(building, on="building_id", how="left")

    if "site_id" not in df.columns:
        raise ValueError(
            "site_id is still missing after merging building metadata. "
            "Check building_metadata columns."
        )

    df = df.merge(weather, on=["site_id", "timestamp"], how="left")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype.name == "category" or df[col].dtype == object:
            df[col] = df[col].astype("category").cat.codes.astype(np.int16)
    return df


def rmsle_logspace(y_true_log: np.ndarray, y_pred_log: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true_log, y_pred_log)))


def load_real_data(
    data_dir: str,
    building_ids: np.ndarray,
    meter: int = 0,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = get_paths(data_dir)

    train_dtypes = {
        "building_id": "int16",
        "meter": "int8",
        "meter_reading": "float32",
        "timestamp": "string",
    }

    log("Loading real BGDP2 train.csv ...")
    real = pd.read_csv(paths["train"], dtype=train_dtypes)
    real = real[real["meter"] == meter].copy()
    real = real[real["building_id"].isin(building_ids)].copy()

    log("Loading weather_train.csv ...")
    weather = pd.read_csv(paths["weather_train"])

    log("Loading building metadata ...")
    building = prepare_building_metadata(load_building_metadata(data_dir))

    return real, weather, building


def find_building_file(directory: str, building_id: int) -> Optional[str]:
    exact_patterns = [
        os.path.join(directory, f"{building_id}.csv"),
        os.path.join(directory, f"{building_id}_*.csv"),
        os.path.join(directory, f"*_{building_id}.csv"),
        os.path.join(directory, f"*_{building_id}_*.csv"),
    ]

    matches = []
    for pattern in exact_patterns:
        matches.extend(glob.glob(pattern))

    matches = sorted(set(matches))
    if not matches:
        return None
    return matches[0]


def normalize_synth_dataframe(df: pd.DataFrame, building_id: int, meter: int) -> pd.DataFrame:
    df = df.copy()

    required = {"timestamp", "value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns {sorted(missing)}")

    df = df.rename(columns={"value": "meter_reading"})
    df["building_id"] = int(building_id)
    df["meter"] = int(meter)

    df = df[["building_id", "meter", "timestamp", "meter_reading"]].copy()
    df["building_id"] = df["building_id"].astype(int)
    df["meter"] = df["meter"].astype(int)
    df["timestamp"] = df["timestamp"].astype(str)
    df["meter_reading"] = pd.to_numeric(df["meter_reading"], errors="coerce").astype("float32")
    df = df.dropna(subset=["timestamp", "meter_reading"])

    return df


def read_single_synth_file(path: str, building_id: int, meter: int = 0) -> pd.DataFrame:
    df = pd.read_csv(path)
    return normalize_synth_dataframe(df, building_id=building_id, meter=meter)


def load_synth_group(
    synth_dir: str,
    building_ids: np.ndarray,
    meter: int = 0,
    require_all_buildings: bool = True,
) -> pd.DataFrame:
    blocks = []
    missing_buildings = []

    log(f"Loading synthetic files from: {synth_dir}")

    for i, bid in enumerate(building_ids, start=1):
        path = find_building_file(synth_dir, int(bid))
        if path is None:
            missing_buildings.append(int(bid))
            log(f"  [{i}/{len(building_ids)}] missing building {bid}")
            continue

        log(f"  [{i}/{len(building_ids)}] reading building {bid}: {os.path.basename(path)}")
        df = read_single_synth_file(path, building_id=int(bid), meter=meter)

        blocks.append(df)

    out = pd.concat(blocks, ignore_index=True)
    log(f"Loaded {len(out):,} synthetic rows from {synth_dir}")
    return out


def ensure_site_id(base: pd.DataFrame, building_meta: pd.DataFrame) -> pd.DataFrame:
    base = base.copy()

    if "site_id" not in base.columns or base["site_id"].isna().any():
        if "site_id" not in building_meta.columns:
            raise ValueError("site_id not found in building metadata")

        site_lookup = building_meta[["building_id", "site_id"]].drop_duplicates()
        base = base.drop(columns=["site_id"], errors="ignore")
        base = base.merge(site_lookup, on="building_id", how="left")

    return base


def make_xy(base: pd.DataFrame, weather: pd.DataFrame, building: pd.DataFrame):
    base = ensure_site_id(base, building)
    base = add_time_features(base)

    weather = weather.copy()
    weather = add_time_features(weather)

    df = merge_all(base, weather, building)

    bids = df["building_id"].astype(int).to_numpy()
    y = np.log1p(df["meter_reading"].values.astype(np.float32))

    df = df.drop(columns=["meter_reading"], errors="ignore")
    df = encode_categoricals(df)
    df = df.drop(columns=["timestamp"], errors="ignore")

    return df, y, bids


def align_feature_columns(train_df: pd.DataFrame, test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    all_cols = sorted(set(train_df.columns) | set(test_df.columns))
    train_aligned = train_df.reindex(columns=all_cols, fill_value=-1)
    test_aligned = test_df.reindex(columns=all_cols, fill_value=-1)
    return train_aligned, test_aligned


def train_lgbm(
    X: pd.DataFrame,
    y: np.ndarray,
    seed: int,
    num_boost_round: int,
    label: str,
) -> lgb.Booster:
    params = {
        "objective": "regression",
        "metric": "rmse",
        "boosting_type": "gbdt",
        "learning_rate": 0.05,
        "num_leaves": 64,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq": 1,
        "min_data_in_leaf": 50,
        "verbosity": -1,
        "seed": seed,
    }

    log(f"Training LightGBM on '{label}' with {len(X):,} rows and {X.shape[1]} features ...")
    dtrain = lgb.Dataset(X, label=y, free_raw_data=False)

    model = lgb.train(
        params,
        dtrain,
        num_boost_round=num_boost_round,
        callbacks=[lgb.log_evaluation(period=200)],
    )
    return model


def per_building_rmsle(
    building_ids: np.ndarray,
    y_true_log: np.ndarray,
    y_pred_log: np.ndarray,
    label: str,
) -> pd.DataFrame:
    df_pb = pd.DataFrame({
        "building_id": building_ids,
        "y_true_log": y_true_log,
        "y_pred_log": y_pred_log,
    })
    pb = (
        df_pb.groupby("building_id")
        .apply(lambda d: float(np.sqrt(mean_squared_error(d["y_true_log"], d["y_pred_log"]))))
        .reset_index()
        .rename(columns={0: "rmsle"})
    )
    pb["training_signal"] = label
    return pb


def save_overall_barplot(summary_df: pd.DataFrame, outpath: str) -> None:
    plot_df = summary_df.sort_values("RMSLE", ascending=True)

    plt.figure(figsize=(10, 5))
    plt.bar(plot_df["Training signal"], plot_df["RMSLE"])
    plt.ylabel("Overall RMSLE")
    plt.title("Overall test RMSLE by training source")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close()


def save_per_building_grouped_barplot(per_building_df: pd.DataFrame, outpath: str) -> None:
    pivot_df = per_building_df.pivot(
        index="building_id",
        columns="training_signal",
        values="rmsle",
    ).sort_index()

    ax = pivot_df.plot(kind="bar", figsize=(14, 6))
    ax.set_xlabel("Building ID")
    ax.set_ylabel("Per-building RMSLE")
    ax.set_title("Per-building RMSLE by training source")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close()


def save_gap_vs_real_plot(per_building_df: pd.DataFrame, outpath: str) -> None:
    pivot_df = per_building_df.pivot(
        index="building_id",
        columns="training_signal",
        values="rmsle",
    ).sort_index()

    if "Real BGDP2" not in pivot_df.columns:
        return

    gap_df = pivot_df.sub(pivot_df["Real BGDP2"], axis=0)
    gap_df = gap_df.drop(columns=["Real BGDP2"], errors="ignore")

    ax = gap_df.plot(kind="bar", figsize=(14, 6))
    ax.set_xlabel("Building ID")
    ax.set_ylabel("RMSLE difference vs real")
    ax.set_title("Per-building RMSLE gap relative to Real BGDP2")
    plt.axhline(0.0, linewidth=1)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(outpath, dpi=200, bbox_inches="tight")
    plt.close()


def build_training_dirs(random_dir: Optional[str]) -> Dict[str, str]:
    training_dirs = dict(SYNTH_DIRS)
    if random_dir:
        training_dirs["Random synthetic"] = random_dir
    return training_dirs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--building-file", required=True)
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--meter", type=int, default=0)
    ap.add_argument("--val-size", type=float, default=0.2)
    ap.add_argument("--n-buildings", type=int, default=15)
    ap.add_argument("--num-boost-round", type=int, default=2000)
    ap.add_argument("--allow-missing-synth-buildings", action="store_true")
    ap.add_argument(
        "--random-dir",
        default=None,
    )
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    synth_dirs = build_training_dirs(args.random_dir)

    log("Starting experiment")
    log(f"data-dir = {args.data_dir}")
    log(f"building-file = {args.building_file}")
    log(f"outdir = {args.outdir}")
    log(f"meter = {args.meter}")
    log(f"n-buildings = {args.n_buildings}")
    log(f"num-boost-round = {args.num_boost_round}")
    if args.random_dir:
        log(f"random-dir = {args.random_dir}")

    building_ids = load_selected_building_ids(args.building_file, n_buildings=args.n_buildings)
    log(f"Using {len(building_ids)} buildings: {building_ids.tolist()}")

    real_raw, weather_train, building_meta = load_real_data(
        args.data_dir,
        building_ids,
        meter=args.meter,
    )

    log(f"Real filtered rows: {len(real_raw):,}")
    X_real, y_real, bids_real = make_xy(real_raw, weather_train, building_meta)
    log(f"Feature matrix shape (real): {X_real.shape}")

    train_idx, test_idx = train_test_split(
        np.arange(len(X_real)),
        test_size=args.val_size,
        random_state=args.seed,
    )

    X_real_train = X_real.iloc[train_idx].copy()
    y_real_train = y_real[train_idx]
    X_real_test = X_real.iloc[test_idx].copy()
    y_real_test = y_real[test_idx]
    real_test_building_id = bids_real[test_idx]

    log(f"Real train rows: {len(X_real_train):,}")
    log(f"Real test rows: {len(X_real_test):,}")

    results = []
    per_building_blocks = []

    log("=== Training on Real BGDP2 ===")
    model_real = train_lgbm(
        X_real_train,
        y_real_train,
        seed=args.seed,
        num_boost_round=args.num_boost_round,
        label="Real BGDP2",
    )
    pred_real = model_real.predict(X_real_test)
    real_score = rmsle_logspace(y_real_test, pred_real)

    results.append({"Training signal": "Real BGDP2", "RMSLE": real_score})
    per_building_blocks.append(
        per_building_rmsle(real_test_building_id, y_real_test, pred_real, "Real BGDP2")
    )
    log(f"Real BGDP2 overall RMSLE = {real_score:.6f}")

    for label, synth_dir in synth_dirs.items():
        log(f"=== Training on {label} ===")

        synth_raw = load_synth_group(
            synth_dir=synth_dir,
            building_ids=building_ids,
            meter=args.meter,
            require_all_buildings=not args.allow_missing_synth_buildings,
        )

        X_synth, y_synth, _ = make_xy(synth_raw, weather_train, building_meta)
        log(f"{label}: raw feature matrix shape = {X_synth.shape}")

        X_synth_aligned, X_test_aligned = align_feature_columns(X_synth, X_real_test)
        log(f"{label}: aligned train shape = {X_synth_aligned.shape}")
        log(f"{label}: aligned test shape  = {X_test_aligned.shape}")

        model = train_lgbm(
            X_synth_aligned,
            y_synth,
            seed=args.seed,
            num_boost_round=args.num_boost_round,
            label=label,
        )

        pred_test = model.predict(X_test_aligned)
        score = rmsle_logspace(y_real_test, pred_test)

        results.append({"Training signal": label, "RMSLE": score})
        per_building_blocks.append(
            per_building_rmsle(real_test_building_id, y_real_test, pred_test, label)
        )

        log(f"{label} overall RMSLE = {score:.6f}")

        del synth_raw, X_synth, y_synth, X_synth_aligned, X_test_aligned, model, pred_test
        gc.collect()

    summary_df = pd.DataFrame(results).sort_values("RMSLE", ascending=True).reset_index(drop=True)

    real_rmsle = float(summary_df.loc[summary_df["Training signal"] == "Real BGDP2", "RMSLE"].iloc[0])
    summary_df["Relative to real (%)"] = 100.0 * (summary_df["RMSLE"] / real_rmsle - 1.0)
    summary_df.loc[summary_df["Training signal"] == "Real BGDP2", "Relative to real (%)"] = np.nan

    per_building_df = pd.concat(per_building_blocks, ignore_index=True)

    pb_real = (
        per_building_df[per_building_df["training_signal"] == "Real BGDP2"][["building_id", "rmsle"]]
        .rename(columns={"rmsle": "real_building_rmsle"})
    )
    per_building_df = per_building_df.merge(pb_real, on="building_id", how="left")
    per_building_df["relative_to_real_pct"] = 100.0 * (
        per_building_df["rmsle"] / per_building_df["real_building_rmsle"] - 1.0
    )
    per_building_df.loc[
        per_building_df["training_signal"] == "Real BGDP2",
        "relative_to_real_pct"
    ] = np.nan

    summary_path = os.path.join(args.outdir, f"building_subset_comparison_{stamp}.csv")
    per_building_path = os.path.join(args.outdir, f"building_subset_per_building_{stamp}.csv")

    summary_df.to_csv(summary_path, index=False)
    per_building_df.to_csv(per_building_path, index=False)

    overall_plot_path = os.path.join(args.outdir, f"overall_rmsle_bar_{stamp}.png")
    per_building_plot_path = os.path.join(args.outdir, f"per_building_rmsle_bar_{stamp}.png")
    gap_plot_path = os.path.join(args.outdir, f"per_building_gap_vs_real_{stamp}.png")

    log("Saving plots ...")
    save_overall_barplot(summary_df, overall_plot_path)
    save_per_building_grouped_barplot(per_building_df, per_building_plot_path)
    save_gap_vs_real_plot(per_building_df, gap_plot_path)

    print("\nSaved files:")
    print(" ", summary_path)
    print(" ", per_building_path)
    print(" ", overall_plot_path)
    print(" ", per_building_plot_path)
    print(" ", gap_plot_path)

    with pd.option_context("display.max_colwidth", 120, "display.width", 180):
        pretty = summary_df.copy()
        pretty["RMSLE"] = pretty["RMSLE"].map(lambda x: f"{x:.4f}")
        pretty["Relative to real (%)"] = pretty["Relative to real (%)"].map(
            lambda x: "--" if pd.isna(x) else f"{x:+.1f}%"
        )
        print("\nOverall results:")
        print(pretty.to_string(index=False))

        pb_pretty = per_building_df[["building_id", "training_signal", "rmsle", "relative_to_real_pct"]].copy()
        pb_pretty["rmsle"] = pb_pretty["rmsle"].map(lambda x: f"{x:.4f}")
        pb_pretty["relative_to_real_pct"] = pb_pretty["relative_to_real_pct"].map(
            lambda x: "--" if pd.isna(x) else f"{x:+.1f}%"
        )
        print("\nPer-building results:")
        print(pb_pretty.to_string(index=False))


if __name__ == "__main__":
    main()
