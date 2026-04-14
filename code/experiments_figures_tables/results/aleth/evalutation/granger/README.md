# Resproduce results for RMSE, MAE, and the Granger statistical test
To run the script, after you have created and installed a virtual environment with necessary dependencies (`pip install -r requirements.txt`), simply run:
```
python rmse_mae_granger_estimator.py.py \
  --real-csvs data/temperature_umurcia_pleiadata/data_files/processed_data/data-roomA-10T.csv data/temperature_umurcia_pleiadata/data_files/processed_data/data-roomB-10T.csv data/temperature_umurcia_pleiadata/data_files/processed_data/data-roomC-10T.csv \
  --gpt-csv gpt_generated_data_from_code/temperature/gpt_oss_office_temperature_2021.csv \
  --aleth-csv aleth_generated_data/temperature/aleth_telemetry_timeseries_temp_murcia.csv \
  --output-csv results_mae_rmse_granger/results_temperature_multiroom.csv \
  --output-dir results_mae_rmse_granger/outputs_multiroom \
  --start 2021-01-01 \
  --end "2021-12-31 23:59:59" \
  --freq 30min \
  --train-frac 0.8 \
  --window-size 48 \
  --fractions 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1 \
  --repeats 10 \
  --random-seed 42 \
  --granger-maxlag 48 \
  --granger-alpha 0.05 \
  --granger-diff
```
