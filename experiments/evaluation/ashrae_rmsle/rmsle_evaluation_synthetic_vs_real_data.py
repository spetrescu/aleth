import os
import argparse
import gc
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple, Optional, List

import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


SUBSET_STATS_CSV = "bgdp2/building_subset_stats_n100_meterall.csv"

SYNTH_DIR = "functional/synth_ale"

SYNTH_FILES = {
    "Random (length/scale matched)": "synthetic_meter_2016_script1_meanonly_20260206_073400.csv",
    "aleth (A) realism only": "synthetic_meter_2016_script2_meta_no_use_20260206_073405.csv",
    "aleth (B) + size context": "synthetic_meter_2016_script3_with_use_20260206_073411.csv",
    "aleth (C) + 1 phenomenon op.": "synthetic_meter_2016_script4_use_plus_weekend20_20260206_073418.csv",
    "aleth (D) full operator set": "synthetic_meter_2016_script5_rich_realism_20260206_073423.csv",
}

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
        bm = pd.read_feather(paths["building_feather"])
    elif os.path.exists(paths["building_csv"]):
        bm = pd.read_csv(paths["building_csv"])
    return bm


def prepare_building_metadata(bm: pd.DataFrame) -> pd.DataFrame:
    if "primary_use" in bm.columns:
        bm["primary_use"] = bm["primary_use"].astype("category")
    if "year_built" in bm.columns:
        bm["year_built"] = bm["year_built"].fillna(bm["year_built"].median())
    if "floor_count" in bm.columns:
        bm["floor_count"] = bm["floor_count"].fillna(bm["floor_count"].median())
    return bm


def add_time_features(df: pd.DataFrame, ts_col: str = "timestamp") -> pd.DataFrame:
    df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce")
    df = df.dropna(subset=[ts_col])
    df["hour"] = df[ts_col].dt.hour.astype(np.int8)
    df["dayofweek"] = df[ts_col].dt.dayofweek.astype(np.int8)
    df["month"] = df[ts_col].dt.month.astype(np.int8)
    df["day"] = df[ts_col].dt.day.astype(np.int8)
    df["weekofyear"] = df[ts_col].dt.isocalendar().week.astype(np.int16)
    return df


def merge_all(base: pd.DataFrame, weather: pd.DataFrame, building: pd.DataFrame) -> pd.DataFrame:
    df = base.merge(building, on="building_id", how="left")
    df = df.merge(weather, on=["site_id", "timestamp"], how="left")
    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype.name == "category" or df[col].dtype == object:
            df[col] = df[col].astype("category").cat.codes.astype(np.int16)
    return df


def rmsle_logspace(y_true_log: np.ndarray, y_pred_log: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true_log, y_pred_log)))

def load_subset_building_ids() -> np.ndarray:
    s = pd.read_csv(SUBSET_STATS_CSV, usecols=["building_id"])
    return s["building_id"].astype(int).unique()


def load_real_data(data_dir: str, building_ids: np.ndarray, meter: int = 0) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = get_paths(data_dir)

    train_dtypes = {
        "building_id": "int16",
        "meter": "int8",
        "site_id": "int8",
        "meter_reading": "float32",
        "timestamp": "string",
    }

    real = pd.read_csv(paths["train"], dtype=train_dtypes)
    real = real[real["meter"] == meter].copy()
    real = real[real["building_id"].isin(building_ids)].copy()

    weather = pd.read_csv(paths["weather_train"])
    building = prepare_building_metadata(load_building_metadata(data_dir))

    return real, weather, building


def load_synth_file(path: str, building_ids: np.ndarray, meter: int = 0) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=["building_id", "meter", "timestamp", "meter_reading"])
    df["building_id"] = df["building_id"].astype(int)
    df["meter"] = df["meter"].astype(int)
    df = df[df["meter"] == meter].copy()
    df = df[df["building_id"].isin(building_ids)].copy()
    return df

def make_xy(base: pd.DataFrame, weather: pd.DataFrame, building: pd.DataFrame):
    base = base.copy()
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

def train_lgbm(X: pd.DataFrame, y: np.ndarray, seed: int, num_boost_round: int) -> lgb.Booster:
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
    dtrain = lgb.Dataset(X, label=y, free_raw_data=False)
    model = lgb.train(params, dtrain, num_boost_round=num_boost_round)
    return model

@dataclass
class ResultRow:
    training_signal: str
    rmsle: float
    rel_to_random_pct: Optional[float]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, help="ASHRAE/BGDP2 directory containing train.csv, weather_train.csv, building_metadata.*")
    ap.add_argument("--outdir", default=".")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--meter", type=int, default=0)
    ap.add_argument("--val-size", type=float, default=0.2)
    ap.add_argument("--num-boost-round", type=int, default=2000, help="Fixed boosting rounds for comparability")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    building_ids = load_subset_building_ids()
    real_raw, weather_train, building_meta = load_real_data(args.data_dir, building_ids, meter=args.meter)

    X_real, y_real, bids_real = make_xy(real_raw, weather_train, building_meta)

    X_real_train, X_real_val, y_real_train, y_real_val = train_test_split(
        X_real, y_real, test_size=args.val_size, random_state=args.seed
    )

    train_idx, val_idx = train_test_split(
    np.arange(len(X_real)),
    test_size=args.val_size,
    random_state=args.seed
    )

    X_real_train = X_real.iloc[train_idx]
    y_real_train = y_real[train_idx]
    X_real_val   = X_real.iloc[val_idx]
    y_real_val   = y_real[val_idx]
    real_val_building_id = bids_real[val_idx]

    real_val_building_id = real_raw.loc[X_real_val.index, "building_id"].astype(int).values

    rows: List[ResultRow] = []
    per_building_blocks = []

    signal_to_rmsle: Dict[str, float] = {}

    for label, fname in SYNTH_FILES.items():
        synth_path = os.path.join(SYNTH_DIR, fname)

        synth_raw = load_synth_file(synth_path, building_ids, meter=args.meter)
        X_synth, y_synth = make_xy(synth_raw, weather_train, building_meta)

        model = train_lgbm(X_synth, y_synth, seed=args.seed, num_boost_round=args.num_boost_round)

        pred_val = model.predict(X_real_val)
        score = rmsle_logspace(y_real_val, pred_val)

        signal_to_rmsle[label] = score
        print(f"{label}: RMSLE={score:.6f}")

        df_pb = pd.DataFrame({
            "building_id": real_val_building_id,
            "y_true_log": y_real_val,
            "y_pred_log": pred_val,
            "file_or_signal": label,
        })
        g = df_pb.groupby("building_id")
        pb = g.apply(lambda d: float(np.sqrt(mean_squared_error(d["y_true_log"], d["y_pred_log"])))).reset_index()
        pb = pb.rename(columns={0: "rmsle"})
        per_building_blocks.append(pb)

        del synth_raw, X_synth, y_synth, model, pred_val, df_pb, g, pb
        gc.collect()

    model_real = train_lgbm(X_real_train, y_real_train, seed=args.seed, num_boost_round=args.num_boost_round)
    pred_real = model_real.predict(X_real_val)
    real_score = rmsle_logspace(y_real_val, pred_real)
    signal_to_rmsle["Real BGDP2 subset (upper bound)"] = real_score
    print(f"[ok] Real BGDP2 subset (upper bound): RMSLE={real_score:.6f}")

    df_pb_real = pd.DataFrame({
        "building_id": real_val_building_id,
        "y_true_log": y_real_val,
        "y_pred_log": pred_real,
        "file_or_signal": "Real BGDP2 subset (upper bound)",
    })
    pb_real = df_pb_real.groupby("building_id").apply(
        lambda d: float(np.sqrt(mean_squared_error(d["y_true_log"], d["y_pred_log"])))
    ).reset_index().rename(columns={0: "rmsle"})
    per_building_blocks.append(pb_real)

    random_key = "Random (length/scale matched)"

    random_rmsle = signal_to_rmsle[random_key]

    ordered_labels = [
        "Random (length/scale matched)",
        "aleth (A) realism only",
        "aleth (B) + size context",
        "aleth (C) + 1 phenomenon op.",
        "aleth (D) full operator set",
        "Real BGDP2 subset (upper bound)",
    ]

    out_rows = []
    for label in ordered_labels:
        s = signal_to_rmsle[label]
        if label == random_key:
            rel = None
        else:
            rel = 100.0 * (s / random_rmsle - 1.0)
        out_rows.append({"Training signal": label, "RMSLE": s, "Relative to random (%)": rel})

    summary_df = pd.DataFrame(out_rows)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = os.path.join(args.outdir, f"functional_realism_rmsle_summary_{stamp}.csv")
    summary_df.to_csv(summary_path, index=False)

    per_building_df = pd.concat(per_building_blocks, ignore_index=True)
    per_building_path = os.path.join(args.outdir, f"functional_realism_rmsle_per_building_{stamp}.csv")
    per_building_df.to_csv(per_building_path, index=False)

    print("\nWrote:")
    print(" ", summary_path)
    print(" ", per_building_path)

    with pd.option_context("display.max_colwidth", 120, "display.width", 160):
        print("\nPaper table preview:")
        pretty = summary_df.copy()
        pretty["RMSLE"] = pretty["RMSLE"].map(lambda x: f"{x:.3f}")
        pretty["Relative to random (%)"] = pretty["Relative to random (%)"].map(
            lambda x: "--" if pd.isna(x) else f"{x:+.1f}%"
        )
        print(pretty.to_string(index=False))

    del X_real, y_real, X_real_train, X_real_val, y_real_train, y_real_val, model_real, pred_real
    gc.collect()


if __name__ == "__main__":
    main()
