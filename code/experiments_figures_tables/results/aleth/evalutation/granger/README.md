# Resproduce results for RMSE, MAE, and the Granger statistical test
Before running the script, make sure you have uncompressed the data (got to the `compressed_data` dir and run `./rebuild_data_files.sh`). Subsequently, to run the experiment script, assuming you have already created and activated a virtual environment (e.g., with `python3 -m venv env` and then `source env/bin/activate`) with necessary dependencies (`pip install -r requirements.txt`), simply run:
```
python granger_estimator.py \
  --real-csvs data/processed_data/data-roomA-10T.csv data/processed_data/data-roomB-10T.csv data/temperature_umurcia_pleiadata/data_files/processed_data/data-roomC-10T.csv \
  --gpt-csv gpt_generated_data_from_code/temperature/gpt_oss_office_temperature_2021.csv \
  --aleth-csv aleth_generated_data/temperature/aleth_telemetry_timeseries_temp_murcia.csv \
  --output-csv results_granger/results_temperature_multiroom.csv \
  --output-dir results_granger/outputs_multiroom \
  --start 2021-01-01 \
  --end "2021-12-31 23:59:59" \
  --freq 30min \
  --train-frac 0.8 \
  --window-size 48 \
  --fractions 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.8 1 \
  --repeats 10 \
  --random-seed 42 \
  --granger-maxlag 48 \
  --granger-alpha 0.05 \
  --granger-diff
```
