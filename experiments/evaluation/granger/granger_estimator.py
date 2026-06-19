from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import matplotlib.ticker as ticker

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, wasserstein_distance
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.stattools import grangercausalitytests

import matplotlib.dates as mdates

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Temperature replacement experiment across multiple real datasets on a common time grid."
    )

    parser.add_argument(
        "--real-csvs",
        type=str,
        nargs="+",
        required=True,
        help="Paths to real PLEIAData CSVs, e.g. roomA roomB roomC."
    )
    parser.add_argument(
        "--gpt-csv",
        type=str,
        required=True,
        help="Path to GPT synthetic CSV."
    )
    parser.add_argument(
        "--aleth-csv",
        type=str,
        required=True,
        help="Path to Aleth synthetic CSV."
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="results_temperature_multiroom.csv",
        help="Path to save cross-room summary CSV."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="experiment_outputs_multiroom",
        help="Directory to save per-room results, diagnostics, and plots."
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Disable saving plots."
    )

    parser.add_argument("--start", type=str, default=None,
                        help="Optional start timestamp, e.g. 2021-01-01")
    parser.add_argument("--end", type=str, default=None,
                        help='Optional end timestamp, e.g. "2021-12-31 23:59:59"')

    parser.add_argument("--real-sep", type=str, default=";",
                        help="CSV separator for real data.")
    parser.add_argument("--real-time-col", type=str, default="Date",
                        help="Timestamp column in real data.")
    parser.add_argument("--real-value-col", type=str, default="V2",
                        help="Temperature column in real data.")

    parser.add_argument("--gpt-time-col", type=str, default="Timestamp",
                        help="Timestamp column in GPT CSV.")
    parser.add_argument("--gpt-value-col", type=str, default="Indoor_Temp_C",
                        help="Temperature column in GPT CSV.")

    parser.add_argument("--aleth-time-col", type=str, default="timestamp",
                        help="Timestamp column in Aleth CSV.")
    parser.add_argument("--aleth-value-col", type=str, default="value",
                        help="Temperature column in Aleth CSV.")

    parser.add_argument("--freq", type=str, default="30min",
                        help="Common frequency, e.g. 30min.")
    parser.add_argument("--agg", type=str, default="mean", choices=["mean", "median"],
                        help="Aggregation used when resampling.")
    parser.add_argument("--tz", type=str, default="UTC",
                        help="Timezone to normalize all timestamps to.")

    parser.add_argument("--train-frac", type=float, default=0.8,
                        help="Fraction of the aligned series used for training.")
    parser.add_argument("--window-size", type=int, default=48,
                        help="Lookback window in timesteps. 48 at 30min = previous 24h.")
    parser.add_argument("--fractions", type=float, nargs="+",
                        default=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0],
                        help="Replacement fractions to evaluate.")
    parser.add_argument("--repeats", type=int, default=10,
                        help="Number of random draws per replacement fraction.")
    parser.add_argument("--random-seed", type=int, default=42,
                        help="Base random seed.")

    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--max-iter", type=int, default=300)
    parser.add_argument("--max-depth", type=int, default=None)
    parser.add_argument("--min-samples-leaf", type=int, default=20)
    parser.add_argument("--l2-regularization", type=float, default=0.0)

    parser.add_argument("--max-train-rows", type=int, default=None,
                        help="Optional cap on train windows for speed.")

    parser.add_argument("--granger-maxlag", type=int, default=48,
                        help="Maximum lag for Granger causality test.")
    parser.add_argument("--granger-alpha", type=float, default=0.05,
                        help="Significance threshold for Granger test.")
    parser.add_argument(
        "--granger-diff",
        action="store_true",
        help="Use first differences before Granger testing (recommended)."
    )

    return parser.parse_args()

COLORS = {
    "real": "#89a54e",
    "gpt": "#e0d3cd",
    "gpt_oss": "#e0d3cd",
    "aleth": "#65cb8c",
    "reference": "#6C757D",
    "default": "#333333",
}

def get_color(name: str) -> str:
    return COLORS.get(name, COLORS["default"])

def ensure_output_dir(path: str) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def infer_room_name(path: str) -> str:
    return Path(path).stem


def parse_timestamps(ts: pd.Series, tz: str) -> pd.DatetimeIndex:
    dt = pd.to_datetime(ts, utc=True, errors="coerce")
    if tz.upper() != "UTC":
        dt = dt.tz_convert(tz)
    return pd.DatetimeIndex(dt)


def apply_time_filter(s: pd.Series, start: str | None, end: str | None, tz: str) -> pd.Series:
    if start is not None:
        start_ts = pd.Timestamp(start, tz=tz if tz.upper() != "UTC" else "UTC")
        s = s[s.index >= start_ts]
    if end is not None:
        end_ts = pd.Timestamp(end, tz=tz if tz.upper() != "UTC" else "UTC")
        s = s[s.index <= end_ts]
    return s


def resample_series(s: pd.Series, freq: str, agg: str) -> pd.Series:
    if agg == "mean":
        return s.resample(freq).mean()
    if agg == "median":
        return s.resample(freq).median()
    raise ValueError(f"Unsupported aggregation: {agg}")


def load_series(
    path: str,
    time_col: str,
    value_col: str,
    sep: str | None,
    freq: str,
    agg: str,
    tz: str,
    name: str,
    start: str | None,
    end: str | None,
) -> pd.Series:
    df = pd.read_csv(path, sep=sep) if sep is not None else pd.read_csv(path)

    if time_col not in df.columns:
        raise ValueError(f"{name}: missing time column '{time_col}'. Columns={list(df.columns)}")
    if value_col not in df.columns:
        raise ValueError(f"{name}: missing value column '{value_col}'. Columns={list(df.columns)}")

    ts = parse_timestamps(df[time_col], tz=tz)
    values = pd.to_numeric(df[value_col], errors="coerce")

    s = pd.Series(values.values, index=ts, name=name)
    s = s[~s.index.isna()].dropna().sort_index()
    s = apply_time_filter(s, start=start, end=end, tz=tz)
    s = resample_series(s, freq=freq, agg=agg).dropna()
    return s


def build_common_dataframe(real_s: pd.Series, gpt_s: pd.Series, aleth_s: pd.Series) -> pd.DataFrame:
    df_all = pd.concat(
        [
            real_s.rename("real"),
            gpt_s.rename("gpt"),
            aleth_s.rename("aleth"),
        ],
        axis=1
    ).dropna().sort_index()
    return df_all


def safe_autocorr(s: pd.Series, lag: int) -> float:
    if len(s) <= lag:
        return float("nan")
    return float(s.autocorr(lag=lag))


def realism_metrics(real_s: pd.Series, synth_s: pd.Series, freq: str) -> Dict[str, float]:
    aligned = pd.concat(
        [real_s.rename("real"), synth_s.rename("synth")],
        axis=1
    ).dropna()

    if len(aligned) == 0:
        raise ValueError("No overlap for realism metrics.")

    real = aligned["real"]
    synth = aligned["synth"]

    q_real = real.quantile([0.1, 0.5, 0.9])
    q_synth = synth.quantile([0.1, 0.5, 0.9])

    ks_stat = ks_2samp(real.to_numpy(), synth.to_numpy()).statistic
    wass = wasserstein_distance(real.to_numpy(), synth.to_numpy())

    diff_real = real.diff().dropna()
    diff_synth = synth.diff().dropna()
    diff_df = pd.concat([diff_real.rename("real"), diff_synth.rename("synth")], axis=1).dropna()
    diff_mae = mean_absolute_error(diff_df["real"], diff_df["synth"]) if len(diff_df) else float("nan")

    steps_per_day = max(1, int(pd.Timedelta("1D") / pd.Timedelta(freq)))
    roll_mean_real = real.rolling(steps_per_day).mean()
    roll_mean_synth = synth.rolling(steps_per_day).mean()
    roll_std_real = real.rolling(steps_per_day).std()
    roll_std_synth = synth.rolling(steps_per_day).std()

    roll_mean_df = pd.concat([roll_mean_real.rename("real"), roll_mean_synth.rename("synth")], axis=1).dropna()
    roll_std_df = pd.concat([roll_std_real.rename("real"), roll_std_synth.rename("synth")], axis=1).dropna()

    roll_mean_mae = mean_absolute_error(roll_mean_df["real"], roll_mean_df["synth"]) if len(roll_mean_df) else float("nan")
    roll_std_mae = mean_absolute_error(roll_std_df["real"], roll_std_df["synth"]) if len(roll_std_df) else float("nan")

    return {
        "raw_mae_vs_real": float(mean_absolute_error(real, synth)),
        "raw_rmse_vs_real": float(math.sqrt(mean_squared_error(real, synth))),
        "raw_corr_vs_real": float(real.corr(synth)),
        "mean_real": float(real.mean()),
        "mean_synth": float(synth.mean()),
        "std_real": float(real.std()),
        "std_synth": float(synth.std()),
        "mean_diff_abs": float(abs(real.mean() - synth.mean())),
        "std_diff_abs": float(abs(real.std() - synth.std())),
        "q10_diff_abs": float(abs(q_real.loc[0.1] - q_synth.loc[0.1])),
        "q50_diff_abs": float(abs(q_real.loc[0.5] - q_synth.loc[0.5])),
        "q90_diff_abs": float(abs(q_real.loc[0.9] - q_synth.loc[0.9])),
        "ks_stat": float(ks_stat),
        "wasserstein": float(wass),
        "acf1_real": safe_autocorr(real, lag=1),
        "acf1_synth": safe_autocorr(synth, lag=1),
        "acf1_diff_abs": float(abs(safe_autocorr(real, lag=1) - safe_autocorr(synth, lag=1))),
        "acf48_real": safe_autocorr(real, lag=48),
        "acf48_synth": safe_autocorr(synth, lag=48),
        "acf48_diff_abs": float(abs(safe_autocorr(real, lag=48) - safe_autocorr(synth, lag=48))),
        "diff_mae": float(diff_mae),
        "rolling24h_mean_mae": float(roll_mean_mae),
        "rolling24h_std_mae": float(roll_std_mae),
        "n_overlap_points": int(len(aligned)),
    }


def raw_fidelity_table(df_all: pd.DataFrame, freq: str) -> pd.DataFrame:
    rows = []
    for col in ["gpt", "aleth"]:
        metrics = realism_metrics(df_all["real"], df_all[col], freq=freq)
        metrics["source"] = col
        rows.append(metrics)
    cols = ["source"] + [c for c in rows[0].keys() if c != "source"]
    return pd.DataFrame(rows)[cols]


def make_supervised(series: pd.Series, window_size: int) -> Tuple[np.ndarray, np.ndarray, pd.DatetimeIndex]:
    values = series.to_numpy(dtype=float)
    idx = series.index

    if len(values) <= window_size:
        raise ValueError(f"Series length {len(values)} must be > window_size {window_size}")

    X, y, y_idx = [], [], []
    for i in range(window_size, len(values)):
        X.append(values[i - window_size:i])
        y.append(values[i])
        y_idx.append(idx[i])

    return np.asarray(X), np.asarray(y), pd.DatetimeIndex(y_idx)


def build_model(args: argparse.Namespace) -> HistGradientBoostingRegressor:
    return HistGradientBoostingRegressor(
        learning_rate=args.learning_rate,
        max_iter=args.max_iter,
        max_depth=args.max_depth,
        min_samples_leaf=args.min_samples_leaf,
        l2_regularization=args.l2_regularization,
        random_state=args.random_seed,
    )


def maybe_subsample_train(
    X_train: np.ndarray,
    y_train: np.ndarray,
    max_rows: int | None,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray]:
    if max_rows is None or len(X_train) <= max_rows:
        return X_train, y_train
    idx = rng.choice(len(X_train), size=max_rows, replace=False)
    idx = np.sort(idx)
    return X_train[idx], y_train[idx]


def evaluate_once(
    aligned_df: pd.DataFrame,
    train_frac: float,
    fraction_replace: float,
    window_size: int,
    model: HistGradientBoostingRegressor,
    rng: np.random.Generator,
    max_train_rows: int | None = None,
) -> Dict[str, float]:
    n = len(aligned_df)
    if n <= window_size + 10:
        raise ValueError(f"Aligned series too short: n={n}, window_size={window_size}")

    split_idx = int(math.floor(n * train_frac))
    if split_idx <= window_size:
        raise ValueError(f"Training split too short: split_idx={split_idx}, window_size={window_size}")
    if split_idx >= n:
        raise ValueError("train_frac leaves no test segment")

    train_real = aligned_df.iloc[:split_idx].copy()
    test_real = aligned_df.iloc[split_idx:].copy()

    n_train = len(train_real)
    n_replace = int(round(fraction_replace * n_train))

    train_modified = train_real["real"].copy()

    if n_replace > 0:
        replace_pos = rng.choice(n_train, size=n_replace, replace=False)
        replace_pos = np.sort(replace_pos)
        replace_idx = train_real.index[replace_pos]
        train_modified.loc[replace_idx] = train_real.loc[replace_idx, "synth"].values

    full_series = pd.concat([
        train_modified.rename("value"),
        test_real["real"].rename("value"),
    ])

    X_all, y_all, y_idx = make_supervised(full_series, window_size=window_size)

    test_start = test_real.index[0]
    train_mask = y_idx < test_start
    test_mask = y_idx >= test_start

    X_train = X_all[train_mask]
    y_train = y_all[train_mask]
    X_test = X_all[test_mask]
    y_test = y_all[test_mask]

    if len(X_train) == 0 or len(X_test) == 0:
        raise ValueError("Empty train or test matrices after windowing")

    X_train, y_train = maybe_subsample_train(X_train, y_train, max_train_rows, rng)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = math.sqrt(mean_squared_error(y_test, y_pred))

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "n_total": int(n),
        "n_train": int(n_train),
        "n_test": int(len(test_real)),
        "n_replace": int(n_replace),
        "n_train_windows": int(len(X_train)),
        "n_test_windows": int(len(X_test)),
        "first_test_timestamp": str(test_real.index[0]),
        "last_test_timestamp": str(test_real.index[-1]),
    }


def run_condition(
    aligned_df: pd.DataFrame,
    condition_name: str,
    fractions: Iterable[float],
    repeats: int,
    args: argparse.Namespace,
    room_name: str,
) -> pd.DataFrame:
    rows: List[Dict[str, float]] = []

    for fraction in fractions:
        for repeat in range(repeats):
            seed = (
                args.random_seed
                + repeat
                + int(round(fraction * 10000))
                + (abs(hash((room_name, condition_name))) % 1_000_000)
            )
            rng = np.random.default_rng(seed)
            model = build_model(args)

            metrics = evaluate_once(
                aligned_df=aligned_df,
                train_frac=args.train_frac,
                fraction_replace=float(fraction),
                window_size=args.window_size,
                model=model,
                rng=rng,
                max_train_rows=args.max_train_rows,
            )
            metrics["condition"] = condition_name
            metrics["fraction_replace"] = float(fraction)
            metrics["repeat"] = int(repeat)
            rows.append(metrics)

    return pd.DataFrame(rows)


def add_baseline_relative_metrics(summary_df: pd.DataFrame) -> pd.DataFrame:
    out = summary_df.copy()

    baseline = (
        out[out["fraction_replace"] == 0.0][["room", "condition", "mae_mean", "rmse_mean"]]
        .rename(columns={
            "mae_mean": "baseline_mae_mean",
            "rmse_mean": "baseline_rmse_mean",
        })
    )

    out = out.merge(baseline, on=["room", "condition"], how="left")

    out["mae_delta_vs_baseline"] = out["mae_mean"] - out["baseline_mae_mean"]
    out["rmse_delta_vs_baseline"] = out["rmse_mean"] - out["baseline_rmse_mean"]

    out["mae_pct_vs_baseline"] = np.where(
        out["baseline_mae_mean"] != 0,
        100.0 * (out["mae_mean"] / out["baseline_mae_mean"] - 1.0),
        np.nan,
    )
    out["rmse_pct_vs_baseline"] = np.where(
        out["baseline_rmse_mean"] != 0,
        100.0 * (out["rmse_mean"] / out["baseline_rmse_mean"] - 1.0),
        np.nan,
    )

    return out


def summarize_results_per_room(results: pd.DataFrame) -> pd.DataFrame:
    summary = (
        results.groupby(["room", "condition", "fraction_replace"], as_index=False)
        .agg(
            mae_mean=("mae", "mean"),
            mae_std=("mae", "std"),
            rmse_mean=("rmse", "mean"),
            rmse_std=("rmse", "std"),
            n_replace_mean=("n_replace", "mean"),
            n_test_windows=("n_test_windows", "mean"),
            repeats=("repeat", "nunique"),
        )
        .sort_values(["room", "condition", "fraction_replace"])
        .reset_index(drop=True)
    )
    return add_baseline_relative_metrics(summary)


def summarize_across_rooms(per_room_summary: pd.DataFrame) -> pd.DataFrame:
    summary = (
        per_room_summary.groupby(["condition", "fraction_replace"], as_index=False)
        .agg(
            mae_mean_across_rooms=("mae_mean", "mean"),
            mae_std_across_rooms=("mae_mean", "std"),
            rmse_mean_across_rooms=("rmse_mean", "mean"),
            rmse_std_across_rooms=("rmse_mean", "std"),
            mae_delta_vs_baseline_mean=("mae_delta_vs_baseline", "mean"),
            mae_delta_vs_baseline_std=("mae_delta_vs_baseline", "std"),
            rmse_delta_vs_baseline_mean=("rmse_delta_vs_baseline", "mean"),
            rmse_delta_vs_baseline_std=("rmse_delta_vs_baseline", "std"),
            mae_pct_vs_baseline_mean=("mae_pct_vs_baseline", "mean"),
            mae_pct_vs_baseline_std=("mae_pct_vs_baseline", "std"),
            rmse_pct_vs_baseline_mean=("rmse_pct_vs_baseline", "mean"),
            rmse_pct_vs_baseline_std=("rmse_pct_vs_baseline", "std"),
            rooms_count=("room", "nunique"),
        )
        .sort_values(["condition", "fraction_replace"])
        .reset_index(drop=True)
    )
    return summary


def summarize_realism_across_rooms(diagnostics_all: pd.DataFrame) -> pd.DataFrame:
    metric_cols = [
        c for c in diagnostics_all.columns
        if c not in {"room", "source"}
    ]

    agg_dict = {}
    for c in metric_cols:
        agg_dict[f"{c}_mean"] = (c, "mean")
        agg_dict[f"{c}_std"] = (c, "std")

    summary = (
        diagnostics_all.groupby(["source"], as_index=False)
        .agg(**agg_dict)
        .sort_values("source")
        .reset_index(drop=True)
    )
    return summary


def prepare_granger_dataframe(
    df_all: pd.DataFrame,
    source_col: str,
    use_diff: bool,
) -> pd.DataFrame:
    """
    Returns a 2-column DataFrame ordered as:
        [real, source]
    which is the order expected by statsmodels for:
        test whether source Granger-causes real
    """
    df = df_all[["real", source_col]].copy()

    if use_diff:
        df = df.diff()

    df = df.dropna()
    return df


def run_granger_one_direction(
    df_all: pd.DataFrame,
    source_col: str,
    maxlag: int,
    alpha: float,
    use_diff: bool,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Tests whether `source_col` Granger-causes `real`.

    statsmodels expects the first column as target/endogenous series and
    the second column as the potential predictor/cause series.
    So to test source -> real, we pass [real, source].
    """
    df_gc = prepare_granger_dataframe(df_all, source_col=source_col, use_diff=use_diff)

    if len(df_gc) <= maxlag + 5:
        raise ValueError(
            f"Not enough rows for Granger test after preprocessing: "
            f"n={len(df_gc)}, maxlag={maxlag}"
        )

    results = grangercausalitytests(df_gc[["real", source_col]], maxlag=maxlag, verbose=False)

    rows = []
    for lag in range(1, maxlag + 1):
        lag_res = results[lag][0]

        ssr_ftest_stat, ssr_ftest_pvalue, ssr_ftest_df_denom, ssr_ftest_df_num = lag_res["ssr_ftest"]
        ssr_chi2test_stat, ssr_chi2test_pvalue, ssr_chi2test_df = lag_res["ssr_chi2test"]
        lrtest_stat, lrtest_pvalue, lrtest_df = lag_res["lrtest"]
        params_ftest_stat, params_ftest_pvalue, params_ftest_df_denom, params_ftest_df_num = lag_res["params_ftest"]

        rows.append({
            "source": source_col,
            "lag": lag,
            "ssr_ftest_stat": float(ssr_ftest_stat),
            "ssr_ftest_pvalue": float(ssr_ftest_pvalue),
            "ssr_ftest_df_denom": float(ssr_ftest_df_denom),
            "ssr_ftest_df_num": float(ssr_ftest_df_num),
            "ssr_chi2test_stat": float(ssr_chi2test_stat),
            "ssr_chi2test_pvalue": float(ssr_chi2test_pvalue),
            "ssr_chi2test_df": float(ssr_chi2test_df),
            "lrtest_stat": float(lrtest_stat),
            "lrtest_pvalue": float(lrtest_pvalue),
            "lrtest_df": float(lrtest_df),
            "params_ftest_stat": float(params_ftest_stat),
            "params_ftest_pvalue": float(params_ftest_pvalue),
            "params_ftest_df_denom": float(params_ftest_df_denom),
            "params_ftest_df_num": float(params_ftest_df_num),
            "significant_at_alpha": bool(ssr_ftest_pvalue < alpha),
            "n_used": int(len(df_gc)),
            "used_first_difference": bool(use_diff),
        })

    per_lag = pd.DataFrame(rows).sort_values("lag").reset_index(drop=True)

    best_idx = per_lag["ssr_ftest_pvalue"].idxmin()
    best_row = per_lag.loc[best_idx]

    summary = {
        "source": source_col,
        "n_used": int(best_row["n_used"]),
        "used_first_difference": bool(best_row["used_first_difference"]),
        "maxlag_tested": int(maxlag),
        "alpha": float(alpha),
        "best_lag_by_pvalue": int(best_row["lag"]),
        "best_ssr_ftest_pvalue": float(best_row["ssr_ftest_pvalue"]),
        "best_ssr_ftest_stat": float(best_row["ssr_ftest_stat"]),
        "any_significant_lag": bool((per_lag["ssr_ftest_pvalue"] < alpha).any()),
        "num_significant_lags": int((per_lag["ssr_ftest_pvalue"] < alpha).sum()),
    }

    return per_lag, summary


def run_granger_comparison(
    df_all: pd.DataFrame,
    maxlag: int,
    alpha: float,
    use_diff: bool,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    per_lag_frames = []
    summary_rows = []

    for source_col in ["gpt", "aleth"]:
        per_lag, summary = run_granger_one_direction(
            df_all=df_all,
            source_col=source_col,
            maxlag=maxlag,
            alpha=alpha,
            use_diff=use_diff,
        )
        per_lag_frames.append(per_lag)
        summary_rows.append(summary)

    per_lag_df = pd.concat(per_lag_frames, ignore_index=True)
    summary_df = pd.DataFrame(summary_rows)

    min_p = summary_df.set_index("source")["best_ssr_ftest_pvalue"].to_dict()
    winner = min(min_p, key=min_p.get)

    summary_df["more_predictive_by_best_pvalue"] = summary_df["source"] == winner
    summary_df["rank_by_best_pvalue"] = summary_df["best_ssr_ftest_pvalue"].rank(method="dense").astype(int)

    return per_lag_df, summary_df


def summarize_granger_across_rooms(granger_summary_all: pd.DataFrame) -> pd.DataFrame:
    out = (
        granger_summary_all.groupby("source", as_index=False)
        .agg(
            rooms_count=("room", "nunique"),
            mean_best_pvalue=("best_ssr_ftest_pvalue", "mean"),
            median_best_pvalue=("best_ssr_ftest_pvalue", "median"),
            mean_best_fstat=("best_ssr_ftest_stat", "mean"),
            mean_best_lag=("best_lag_by_pvalue", "mean"),
            rooms_with_any_significant_lag=("any_significant_lag", "sum"),
            total_significant_lags=("num_significant_lags", "sum"),
            wins_by_best_pvalue=("more_predictive_by_best_pvalue", "sum"),
        )
        .sort_values(["mean_best_pvalue", "source"])
        .reset_index(drop=True)
    )
    return out

def _import_plt():
    import matplotlib.pyplot as plt
    return plt


def _safe_filename(text: str) -> str:
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in text)


def save_aligned_series_plots(df_all: pd.DataFrame, output_dir: Path) -> None:
    plt = _import_plt()

    

    plt.figure(figsize=(5, 4))

    plt.plot(df_all.index, df_all["real"], label="real", linewidth=1.0, color=get_color("real"))
    plt.plot(df_all.index, df_all["gpt"], label="gpt_oss", linewidth=1.0, alpha=0.8, color=get_color("gpt"))
    plt.plot(df_all.index, df_all["aleth"], label="aleth", linewidth=1.0, alpha=0.8, color=get_color("aleth"))

    ax = plt.gca()

    locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
    formatter = mdates.ConciseDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.tick_params(axis='both', labelsize=12)
    ax.tick_params(axis='x', labelsize=12)

    plt.title("Example real (RoomA-10T) vs. aleth vs. LLM code-generated data", fontsize=9)
    plt.xlabel("Time")
    plt.ylabel("Temperature")
    plt.legend()
    plt.tight_layout()
    legend = ax.legend()
    for line in legend.get_lines():
        line.set_linewidth(2.1)
    plt.savefig(output_dir / "aligned_series.pdf", dpi=160)
    plt.close()

    first_week_end = df_all.index.min() + pd.Timedelta(days=7)
    df_week = df_all[df_all.index <= first_week_end]
    if len(df_week) > 0:
        plt.figure(figsize=(15, 5))
        plt.plot(df_week.index, df_week["real"], label="real", linewidth=1.2)
        plt.plot(df_week.index, df_week["gpt"], label="gpt-oss", linewidth=1.2, alpha=0.8)
        plt.plot(df_week.index, df_week["aleth"], label="aleth", linewidth=1.2, alpha=0.8)
        plt.title("Temperature series on common overlap: first 7 days")
        plt.xlabel("Time")
        plt.ylabel("Temperature")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / "aligned_series_first_week.png", dpi=160)
        plt.close()


def save_distribution_plots(df_all: pd.DataFrame, output_dir: Path) -> None:
    plt = _import_plt()

    for col in ["real", "gpt", "aleth"]:
        plt.figure(figsize=(7, 4.5))
        plt.hist(df_all[col].dropna(), bins=40, alpha=0.8)
        plt.title(f"Distribution: {col}")
        plt.xlabel("Temperature")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(output_dir / f"hist_{col}.png", dpi=160)
        plt.close()

    plt.figure(figsize=(7, 4.5))
    plt.hist(df_all["real"].dropna(), bins=40, alpha=0.5, label="real")
    plt.hist(df_all["gpt"].dropna(), bins=40, alpha=0.5, label="gpt_oss")
    plt.hist(df_all["aleth"].dropna(), bins=40, alpha=0.5, label="aleth")
    plt.title("Distribution comparison")
    plt.xlabel("Temperature")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "hist_overlay.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 4.5))
    plt.boxplot(
        [
            df_all["real"].dropna().values,
            df_all["gpt"].dropna().values,
            df_all["aleth"].dropna().values,
        ],
        labels=["real", "gpt_oss", "aleth"],
    )
    plt.title("Temperature boxplots")
    plt.ylabel("Temperature")
    plt.tight_layout()
    plt.savefig(output_dir / "boxplots.png", dpi=160)
    plt.close()


def save_fidelity_bar_plots(diagnostics: pd.DataFrame, output_dir: Path) -> None:
    plt = _import_plt()

    metrics_to_plot = [
        "raw_mae_vs_real",
        "raw_rmse_vs_real",
        "raw_corr_vs_real",
        "ks_stat",
        "wasserstein",
        "diff_mae",
        "rolling24h_mean_mae",
        "rolling24h_std_mae",
        "acf1_diff_abs",
        "acf48_diff_abs",
    ]

    for metric in metrics_to_plot:
        if metric not in diagnostics.columns:
            continue

        sub = diagnostics[["source", metric]].copy()

        plt.figure(figsize=(6, 4))
        plt.bar(sub["source"], sub[metric])
        plt.title(metric)
        plt.xlabel("Source")
        plt.ylabel(metric)
        plt.tight_layout()
        plt.savefig(output_dir / f"fidelity_{_safe_filename(metric)}.png", dpi=160)
        plt.close()


def save_result_plots(summary: pd.DataFrame, output_dir: Path, no_plots: bool, prefix: str = "") -> None:
    if no_plots:
        return

    plt = _import_plt()

    if prefix:
        prefix = f"{prefix}_"

    if "mae_mean" in summary.columns:
        mae_col = "mae_mean"
        mae_err = "mae_std"
        rmse_col = "rmse_mean"
        rmse_err = "rmse_std"
        mae_delta_col = "mae_delta_vs_baseline"
        rmse_delta_col = "rmse_delta_vs_baseline"
        mae_pct_col = "mae_pct_vs_baseline"
        rmse_pct_col = "rmse_pct_vs_baseline"
    else:
        mae_col = "mae_mean_across_rooms"
        mae_err = "mae_std_across_rooms"
        rmse_col = "rmse_mean_across_rooms"
        rmse_err = "rmse_std_across_rooms"
        mae_delta_col = "mae_delta_vs_baseline_mean"
        rmse_delta_col = "rmse_delta_vs_baseline_mean"
        mae_pct_col = "mae_pct_vs_baseline_mean"
        rmse_pct_col = "rmse_pct_vs_baseline_mean"

    for metric_name, mean_col, err_col in [
        ("mae", mae_col, mae_err),
        ("rmse", rmse_col, rmse_err),
    ]:
        plt.figure(figsize=(7, 4.5))
        for cond in summary["condition"].unique():
            sub = summary[summary["condition"] == cond].sort_values("fraction_replace")
            plt.errorbar(
                sub["fraction_replace"],
                sub[mean_col],
                yerr=sub[err_col].fillna(0.0),
                marker="o",
                capsize=3,
                label=cond,
            )
        plt.xlabel("Replacement fraction")
        plt.ylabel(metric_name.upper())
        plt.title(f"{metric_name.upper()} vs replacement fraction")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"{prefix}{metric_name}_vs_fraction.png", dpi=160)
        plt.close()

    for metric_name, col in [
        ("mae_delta_vs_baseline", mae_delta_col),
        ("rmse_delta_vs_baseline", rmse_delta_col),
        ("mae_pct_vs_baseline", mae_pct_col),
        ("rmse_pct_vs_baseline", rmse_pct_col),
    ]:
        if col not in summary.columns:
            continue

        plt.figure(figsize=(7, 4.5))
        for cond in summary["condition"].unique():
            sub = summary[summary["condition"] == cond].sort_values("fraction_replace")
            plt.plot(
                sub["fraction_replace"],
                sub[col],
                marker="o",
                label=cond,
            )
        plt.axhline(0.0, linestyle="--", linewidth=1.0)
        plt.xlabel("Replacement fraction")
        plt.ylabel(metric_name)
        plt.title(metric_name.replace("_", " "))
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"{prefix}{metric_name}.png", dpi=160)
        plt.close()


def save_per_run_spread_plots(results: pd.DataFrame, output_dir: Path) -> None:
    plt = _import_plt()

    for metric in ["mae", "rmse"]:
        plt.figure(figsize=(8, 5))
        for cond in results["condition"].unique():
            sub = results[results["condition"] == cond]
            grouped = sub.groupby("fraction_replace")[metric]
            x = []
            y = []
            for frac, vals in grouped:
                x.extend([frac] * len(vals))
                y.extend(vals.tolist())
            plt.scatter(x, y, alpha=0.6, label=cond)
        plt.xlabel("Replacement fraction")
        plt.ylabel(metric.upper())
        plt.title(f"Per-run {metric.upper()} spread")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"per_run_{metric}_spread.png", dpi=160)
        plt.close()


def save_granger_plots(
    granger_per_lag: pd.DataFrame,
    granger_summary: pd.DataFrame,
    output_dir: Path,
    alpha: float,
    prefix: str = "",
) -> None:
    plt = _import_plt()

    if prefix:
        prefix = f"{prefix}_"

    plt.figure(figsize=(8, 5))
    for source in granger_per_lag["source"].unique():
        sub = granger_per_lag[granger_per_lag["source"] == source].sort_values("lag")
        plt.plot(sub["lag"], sub["ssr_ftest_pvalue"], marker="o", label=source)
    plt.axhline(alpha, linestyle="--", linewidth=1.0, label=f"alpha={alpha}")
    plt.xlabel("Lag")
    plt.ylabel("SSR F-test p-value")
    plt.title("Granger causality p-values by lag")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / f"{prefix}granger_pvalues_by_lag.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    for source in granger_per_lag["source"].unique():
        sub = granger_per_lag[granger_per_lag["source"] == source].sort_values("lag")
        plt.plot(sub["lag"], sub["ssr_ftest_stat"], marker="o", label=source)
    plt.xlabel("Lag")
    plt.ylabel("SSR F-test statistic")
    plt.title("Granger causality F-statistics by lag")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / f"{prefix}granger_fstats_by_lag.png", dpi=160)
    plt.close()

    summary_plot_cols = [
        "best_ssr_ftest_pvalue",
        "best_ssr_ftest_stat",
        "best_lag_by_pvalue",
        "num_significant_lags",
    ]

    for col in summary_plot_cols:
        if col not in granger_summary.columns:
            continue
        plt.figure(figsize=(6, 4))
        plt.bar(granger_summary["source"], granger_summary[col])
        plt.title(col)
        plt.xlabel("Source")
        plt.ylabel(col)
        plt.tight_layout()
        plt.savefig(output_dir / f"{prefix}granger_summary_{_safe_filename(col)}.png", dpi=160)
        plt.close()


def save_cross_room_granger_plots(granger_cross_room_summary: pd.DataFrame, output_dir: Path) -> None:
    plt = _import_plt()

    metrics = [
        "mean_best_pvalue",
        "median_best_pvalue",
        "mean_best_fstat",
        "mean_best_lag",
        "rooms_with_any_significant_lag",
        "total_significant_lags",
        "wins_by_best_pvalue",
    ]

    for metric in metrics:
        if metric not in granger_cross_room_summary.columns:
            continue
        plt.figure(figsize=(7, 4.5))
        plt.bar(granger_cross_room_summary["source"], granger_cross_room_summary[metric])
        plt.title(f"Cross-room Granger summary: {metric}")
        plt.xlabel("Source")
        plt.ylabel(metric)
        plt.tight_layout()
        plt.savefig(output_dir / f"cross_room_granger_{_safe_filename(metric)}.png", dpi=160)
        plt.close()


def save_realism_summary_plots(realism_summary: pd.DataFrame, output_dir: Path) -> None:
    plt = _import_plt()

    candidate_cols = [
        "raw_mae_vs_real_mean",
        "raw_rmse_vs_real_mean",
        "raw_corr_vs_real_mean",
        "ks_stat_mean",
        "wasserstein_mean",
        "diff_mae_mean",
        "rolling24h_mean_mae_mean",
        "rolling24h_std_mae_mean",
        "acf1_diff_abs_mean",
        "acf48_diff_abs_mean",
    ]

    for col in candidate_cols:
        if col not in realism_summary.columns:
            continue
        plt.figure(figsize=(7, 4.5))
        plt.bar(realism_summary["source"], realism_summary[col])
        plt.title(f"Realism summary: {col}")
        plt.xlabel("Source")
        plt.ylabel(col)
        plt.tight_layout()
        plt.savefig(output_dir / f"realism_summary_{_safe_filename(col)}.png", dpi=160)
        plt.close()


def save_diagnostics(df_all: pd.DataFrame, diagnostics: pd.DataFrame, output_dir: Path, no_plots: bool) -> None:
    diagnostics.to_csv(output_dir / "raw_fidelity_diagnostics.csv", index=False)

    if no_plots:
        return

    save_aligned_series_plots(df_all, output_dir)
    save_distribution_plots(df_all, output_dir)
    save_fidelity_bar_plots(diagnostics, output_dir)


def run_single_room_experiment(
    real_csv: str,
    gpt_s: pd.Series,
    aleth_s: pd.Series,
    args: argparse.Namespace,
    base_output_dir: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    room_name = infer_room_name(real_csv)
    room_output_dir = base_output_dir / room_name
    room_output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 80}")
    print(f"Running room: {room_name}")
    print(f"Real CSV: {real_csv}")

    real_s = load_series(
        path=real_csv,
        time_col=args.real_time_col,
        value_col=args.real_value_col,
        sep=args.real_sep,
        freq=args.freq,
        agg=args.agg,
        tz=args.tz,
        name="real",
        start=args.start,
        end=args.end,
    )

    print(f"Real series length after resampling   : {len(real_s)}")
    print(f"GPT series length after resampling    : {len(gpt_s)}")
    print(f"Aleth series length after resampling  : {len(aleth_s)}")

    df_all = build_common_dataframe(real_s, gpt_s, aleth_s)

    print(f"Common aligned length: {len(df_all)}")
    print(f"Aligned start: {df_all.index.min()}")
    print(f"Aligned end  : {df_all.index.max()}")

    diagnostics = raw_fidelity_table(df_all, freq=args.freq)
    diagnostics.insert(0, "room", room_name)
    save_diagnostics(df_all, diagnostics, room_output_dir, args.no_plots)

    print("Running Granger causality comparison...")
    granger_per_lag, granger_summary = run_granger_comparison(
        df_all=df_all,
        maxlag=args.granger_maxlag,
        alpha=args.granger_alpha,
        use_diff=args.granger_diff,
    )
    granger_per_lag.insert(0, "room", room_name)
    granger_summary.insert(0, "room", room_name)

    granger_per_lag.to_csv(room_output_dir / "granger_per_lag.csv", index=False)
    granger_summary.to_csv(room_output_dir / "granger_summary.csv", index=False)

    if not args.no_plots:
        save_granger_plots(
            granger_per_lag=granger_per_lag.drop(columns=["room"]),
            granger_summary=granger_summary.drop(columns=["room"]),
            output_dir=room_output_dir,
            alpha=args.granger_alpha,
        )

    aligned_gpt = df_all[["real", "gpt"]].rename(columns={"gpt": "synth"})
    aligned_aleth = df_all[["real", "aleth"]].rename(columns={"aleth": "synth"})

    print("Running GPT replacement condition...")
    results_gpt = run_condition(
        aligned_df=aligned_gpt,
        condition_name="gpt_oss",
        fractions=args.fractions,
        repeats=args.repeats,
        args=args,
        room_name=room_name,
    )

    print("Running Aleth replacement condition...")
    results_aleth = run_condition(
        aligned_df=aligned_aleth,
        condition_name="aleth",
        fractions=args.fractions,
        repeats=args.repeats,
        args=args,
        room_name=room_name,
    )

    results = pd.concat([results_gpt, results_aleth], ignore_index=True)
    results.insert(0, "room", room_name)

    room_summary = summarize_results_per_room(results)

    room_summary_path = room_output_dir / "summary.csv"
    room_per_run_path = room_output_dir / "results_per_run.csv"
    room_diag_path = room_output_dir / "raw_fidelity_diagnostics.csv"

    room_summary.to_csv(room_summary_path, index=False)
    results.to_csv(room_per_run_path, index=False)
    diagnostics.to_csv(room_diag_path, index=False)

    if not args.no_plots:
        save_result_plots(room_summary.drop(columns=["room"]), room_output_dir, args.no_plots)
        save_per_run_spread_plots(results.drop(columns=["room"]), room_output_dir)

    print("\nRoom summary:")
    print(room_summary.to_string(index=False))

    print("\nRoom Granger summary:")
    print(granger_summary.to_string(index=False))

    print(f"Saved room summary to: {room_summary_path}")
    print(f"Saved room per-run results to: {room_per_run_path}")
    print(f"Saved room diagnostics/plots to: {room_output_dir}")
    print(f"Saved room Granger per-lag results to: {room_output_dir / 'granger_per_lag.csv'}")
    print(f"Saved room Granger summary to: {room_output_dir / 'granger_summary.csv'}")

    return results, room_summary, diagnostics, granger_summary


def main() -> None:
    args = parse_args()
    output_dir = ensure_output_dir(args.output_dir)

    print("Loading shared synthetic series...")
    gpt_s = load_series(
        path=args.gpt_csv,
        time_col=args.gpt_time_col,
        value_col=args.gpt_value_col,
        sep=None,
        freq=args.freq,
        agg=args.agg,
        tz=args.tz,
        name="gpt",
        start=args.start,
        end=args.end,
    )
    aleth_s = load_series(
        path=args.aleth_csv,
        time_col=args.aleth_time_col,
        value_col=args.aleth_value_col,
        sep=None,
        freq=args.freq,
        agg=args.agg,
        tz=args.tz,
        name="aleth",
        start=args.start,
        end=args.end,
    )

    all_results = []
    all_room_summaries = []
    all_diagnostics = []
    all_granger_summaries = []

    for real_csv in args.real_csvs:
        real_path = Path(real_csv)
        if not real_path.exists():
            raise FileNotFoundError(f"Real CSV not found: {real_csv}")

        results, room_summary, diagnostics, granger_summary = run_single_room_experiment(
            real_csv=real_csv,
            gpt_s=gpt_s,
            aleth_s=aleth_s,
            args=args,
            base_output_dir=output_dir,
        )
        all_results.append(results)
        all_room_summaries.append(room_summary)
        all_diagnostics.append(diagnostics)
        all_granger_summaries.append(granger_summary)

    results_all = pd.concat(all_results, ignore_index=True)
    per_room_summary = pd.concat(all_room_summaries, ignore_index=True)
    diagnostics_all = pd.concat(all_diagnostics, ignore_index=True)
    granger_summary_all = pd.concat(all_granger_summaries, ignore_index=True)

    cross_room_summary = summarize_across_rooms(per_room_summary)
    realism_summary = summarize_realism_across_rooms(diagnostics_all)
    granger_cross_room_summary = summarize_granger_across_rooms(granger_summary_all)

    output_csv = Path(args.output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    per_run_path = output_dir / "results_per_run_all_rooms.csv"
    per_room_summary_path = output_dir / "summary_per_room.csv"
    diagnostics_path = output_dir / "raw_fidelity_diagnostics_all_rooms.csv"
    realism_summary_path = output_dir / "realism_summary_across_rooms.csv"
    granger_summary_path = output_dir / "granger_summary_all_rooms.csv"
    granger_cross_room_summary_path = output_dir / "granger_cross_room_summary.csv"
    cross_room_summary_path = output_csv

    results_all.to_csv(per_run_path, index=False)
    per_room_summary.to_csv(per_room_summary_path, index=False)
    diagnostics_all.to_csv(diagnostics_path, index=False)
    realism_summary.to_csv(realism_summary_path, index=False)
    granger_summary_all.to_csv(granger_summary_path, index=False)
    granger_cross_room_summary.to_csv(granger_cross_room_summary_path, index=False)
    cross_room_summary.to_csv(cross_room_summary_path, index=False)

    if not args.no_plots:
        save_result_plots(cross_room_summary, output_dir, args.no_plots, prefix="cross_room")
        save_cross_room_granger_plots(granger_cross_room_summary, output_dir)
        save_realism_summary_plots(realism_summary, output_dir)

    print(f"\n{'=' * 80}")
    print("CROSS-ROOM UTILITY SUMMARY:")
    print(cross_room_summary.to_string(index=False))

    print(f"\nREALISM SUMMARY ACROSS ROOMS:")
    print(realism_summary.to_string(index=False))

    print(f"\nGRANGER SUMMARY ACROSS ROOMS:")
    print(granger_cross_room_summary.to_string(index=False))

    print(f"\nSaved cross-room summary to: {cross_room_summary_path}")
    print(f"Saved all per-run results to: {per_run_path}")
    print(f"Saved per-room summary to: {per_room_summary_path}")
    print(f"Saved all diagnostics to: {diagnostics_path}")
    print(f"Saved realism summary to: {realism_summary_path}")
    print(f"Saved all Granger summaries to: {granger_summary_path}")
    print(f"Saved cross-room Granger summary to: {granger_cross_room_summary_path}")
    print(f"Saved plots to: {output_dir}")


if __name__ == "__main__":
    main()
  
