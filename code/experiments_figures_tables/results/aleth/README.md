# aleth

## Running `aleth`
To run aleth (assuming you have deployed `ollama` -- see instructions below), simply follow these steps:
### 1/2 Virtual environment
Assuming you have `venv` installed, first create a virtual environment to install dependencies required to run code. Therefore:
1.  Run `python3 -m venv env-aleth`
2. Run `source env-aleth/bin/activate`
3. Lastly, navigate to `src/aleth` and run `pip install .`
### 2/2 Run `aleth`
Simply run `aleth` using: 
```
aleth --scenario "Give me sensor data for a small office electricity usage" --progress
```

## Evaluation scripts for `aleth`
To reproduce results for the `granger` and `ashrae_rmsle` experiments navigate to the evaluation folder.

## Hardware
All tests were run on two servers: a single-GPU node with an `NVIDIA RTX PRO 6000 (96GB VRAM)` and an `AMD EPYC 9354P CPU (32 cores)`, and a `Dell PowerEdge` server equipped with two `NVIDIA RTX A5000 GPUs (24GB VRAM each)` - both with `Ubuntu 24.04.3 LTS` installed.

## Prerequisite - serve `ollama`
Across experiments that use LLMs, we used `ollama` for serving the models. There are two main things you have to ensure regarding `ollama`, namely that the ollama server is running with the right configuration and that the model you are trying to run is actually downloaded on the machine. For `aleth`, we have used `gpt-oss` as a backend model, but this can also be changed in the configuration parameters (in case you want to explore or update the backend model in terms of how well it parses the intent or generates the points -- this can be found in the `aleth/config.py` file, where currently both models are pointing to the same model `MAIN_MODEL_INTENT_PARSING = "gpt-oss:20b"` and `MAIN_MODEL_RANGE_ESTIMATOR = "gpt-oss:20b"`). Now, going back to `ollama`:

1. For the former (serving ollama), after you have installed `ollama` ([https://ollama.com/download/linux](https://ollama.com/download/linux)), make sure you run it with the following command: `OLLAMA_CONTEXT_LENGTH=64000 ollama serve &`. This ensure that the model runs with 64k as context instead of the default 2048.

2. For the latter (downloading models), assuming you have successfully managed to serve ollama, to download models of your choice simply run: `ollama pull <model>`, for example: `ollama pull gpt-oss:20b`. This command is actually sufficient (as this is the main model we use behind the scenes for `aleth`). To see that `ollama` is started in the background, simply test this by running `ollama ps` in another terminal.

After you have followed the two steps above, you should be setup for success with interfacing with ollama in order to reproduce experiments that use LLMs.

## Data
In the paper, we have used two main datasets for evaluation of data realism of `aleth` -- BGDP2 (for electricity) and PLEIAData (for temperature, CO2, and PIR). Before running the code, make sure you pull the data to your machine (and also have deployed `ollama` as a daemon -- see instructions above). We provide instructions below on how to do that:

### BGDP2
The ASHRAE Great Energy Predictor III dataset contains three years of hourly energy consumption data for over 1,000 buildings across multiple sites worldwide. It combines meter readings (electricity, chilled water, steam, and hot water) with building metadata and local weather observations, making it well-suited for time-series forecasting and energy efficiency modeling tasks. Speicifically, the dataset is from the publicly available resoource at [https://www.kaggle.com/datasets/claytonmiller/buildingdatagenomeproject2](https://www.kaggle.com/datasets/claytonmiller/buildingdatagenomeproject2). <br>

The dataset is stored as split archive parts under `archive_files/` due to GitHub’s 100MB file limit. You have to navigate to the root of the repository to access it.
To rebuild the original files, run:
1:
```bash
cd archive_files
```
2: 
```bash
bash rebuild_data_files.sh
```
Before running the bash script, make sure it is executable (you can run `chmod +x rebuild_data_files.sh`)

### PLEIAData
According to the official Zenodo resource (https://zenodo.org/records/7620136):
"This dataset presents detailed building operation data from the three blocks (A, B and C) of the Pleiades building of the University of Murcia, which is a pilot building of the European project PHOENIX. The aim of PHOENIX is to improve buildings efficiency, and therefore we included information of: (i) consumption data, aggregated by block in kWh; (ii) HVAC (Heating, Ventilation and Air Conditioning) data with several features, such as state (ON=1, OFF=0), operation mode (None=0, Heating=1, Cooling=2), setpoint and device type; (iii) indoor temperature  per room; (iv) weather data, including temperature, humidity, radiation, dew point, wind direction and precipitation; (v) carbon dioxide and presence data for few rooms; (vi) relationships between HVAC, temperature, carbon dioxide and presence sensors identifiers with their respective rooms and blocks. Weather data was acquired from the IMIDA (Instituto Murciano de Investigación y Desarrollo Agrario y Alimentario)."

## Reconstructing the dataset
The dataset is stored as split archive parts under `archive_files/` due to GitHub’s 100MB file limit. Again, you have to navigate to the root of the repository to access it.
To rebuild the original files, run:
1:
```bash
cd archive_files
```
2: 
```bash
bash rebuild_data_files.sh
```
Before running the bash script, make sure it is executable (you can run `chmod +x rebuild_data_files.sh`)

## Example execution
```
$ aleth --scenario "office electricity usage" --progress --tqdm
Hierarchy generation:   0%|                                                                                 | 0/432 [00:00<?, ?step/s][2026-03-17T19:15:12] [INFO] [init] run_start | scenario='office electricity usage', years=[2025], unit_hint=kW, model=gpt-oss:20b | progress=0/432 (0.00%)
[2026-03-17T19:15:16] [INFO] [init] simulation_intent | modality=electricity, granularity_minutes=60, horizon_years=1, precision_decimals=2, outage_pct=0.0, hw_error_pct=0.0 | progress=0/432 (0.00%)
[2026-03-17T19:15:16] [INFO] [modality_profile] stage_start | deriving modality behavior | progress=0/432 (0.00%)
[2026-03-17T19:15:16] [INFO] [modality_profile] llm_attempt | attempt 1/3 | progress=0/432 (0.00%)
[2026-03-17T19:15:20] [INFO] [modality_profile] llm_success | duration=3.83s | cum_llm=3.83s | progress=0/432 (0.00%)
Hierarchy generation:   0%|                                     | 1/432 [00:07<53:51,  7.50s/step, profile family=electricity unit=kW][2026-03-17T19:15:20] [INFO] [modality_profile] step_done | profile family=electricity unit=kW | progress=1/432 (0.23%)
[2026-03-17T19:15:20] [INFO] [year_ranges] stage_start | years=[2025] | progress=1/432 (0.23%)
[2026-03-17T19:15:20] [INFO] [year_ranges] llm_attempt | attempt 1/3 | progress=1/432 (0.23%)
[2026-03-17T19:15:27] [INFO] [year_ranges] llm_success | duration=7.27s | cum_llm=11.10s | progress=1/432 (0.23%)
Hierarchy generation:   0%|▏                                               | 2/432 [00:14<52:47,  7.37s/step, generated 1 year ranges][2026-03-17T19:15:27] [INFO] [year_ranges] step_done | generated 1 year ranges | progress=2/432 (0.46%)
[2026-03-17T19:15:27] [INFO] [season_ranges] stage_start | year=2025 | progress=2/432 (0.46%)
[2026-03-17T19:15:27] [INFO] [season_ranges] llm_attempt | attempt 1/3 | progress=2/432 (0.46%)
[2026-03-17T19:15:34] [INFO] [season_ranges] llm_success | duration=7.09s | cum_llm=18.19s | progress=2/432 (0.46%)
Hierarchy generation:   1%|▎                                                   | 3/432 [00:21<51:45,  7.24s/step, year=2025 seasons=4][2026-03-17T19:15:34] [INFO] [season_ranges] step_done | year=2025 seasons=4 | progress=3/432 (0.69%)
[2026-03-17T19:15:34] [INFO] [month_ranges] stage_start | year=2025 season=winter months=[1, 2, 12] | progress=3/432 (0.69%)
[2026-03-17T19:15:34] [INFO] [month_ranges] llm_attempt | attempt 1/3 | progress=3/432 (0.69%)
[2026-03-17T19:15:40] [INFO] [month_ranges] llm_success | duration=5.65s | cum_llm=23.84s | progress=3/432 (0.69%)
Hierarchy generation:   1%|▎                                      | 4/432 [00:27<47:09,  6.61s/step, year=2025 season=winter months=3][2026-03-17T19:15:40] [INFO] [month_ranges] step_done | year=2025 season=winter months=3 | progress=4/432 (0.93%)
[2026-03-17T19:15:40] [INFO] [month_ranges] stage_start | year=2025 season=spring months=[3, 4, 5] | progress=4/432 (0.93%)
[2026-03-17T19:15:40] [INFO] [month_ranges] llm_attempt | attempt 1/3 | progress=4/432 (0.93%)
[2026-03-17T19:15:45] [INFO] [month_ranges] llm_success | duration=5.67s | cum_llm=29.51s | progress=4/432 (0.93%)
Hierarchy generation:   1%|▍                                      | 5/432 [00:33<44:38,  6.27s/step, year=2025 season=spring months=3][2026-03-17T19:15:45] [INFO] [month_ranges] step_done | year=2025 season=spring months=3 | progress=5/432 (1.16%)
[2026-03-17T19:15:45] [INFO] [month_ranges] stage_start | year=2025 season=summer months=[6, 7, 8] | progress=5/432 (1.16%)
[2026-03-17T19:15:45] [INFO] [month_ranges] llm_attempt | attempt 1/3 | progress=5/432 (1.16%)
[2026-03-17T19:15:53] [INFO] [month_ranges] llm_success | duration=7.13s | cum_llm=36.64s | progress=5/432 (1.16%)
Hierarchy generation:   1%|▌                                      | 6/432 [00:40<46:36,  6.57s/step, year=2025 season=summer months=3][2026-03-17T19:15:53] [INFO] [month_ranges] step_done | year=2025 season=summer months=3 | progress=6/432 (1.39%)
[2026-03-17T19:15:53] [INFO] [month_ranges] stage_start | year=2025 season=autumn months=[9, 10, 11] | progress=6/432 (1.39%)
[2026-03-17T19:15:53] [INFO] [month_ranges] llm_attempt | attempt 1/3 | progress=6/432 (1.39%)
[2026-03-17T19:15:59] [INFO] [month_ranges] llm_success | duration=6.14s | cum_llm=42.79s | progress=6/432 (1.39%)
Hierarchy generation:   2%|▋                                      | 7/432 [00:46<45:31,  6.43s/step, year=2025 season=autumn months=3][2026-03-17T19:15:59] [INFO] [month_ranges] step_done | year=2025 season=autumn months=3 | progress=7/432 (1.62%)
[2026-03-17T19:15:59] [INFO] [week_ranges] stage_start | year=2025 month=1 | progress=7/432 (1.62%)
[2026-03-17T19:15:59] [INFO] [week_ranges] llm_attempt | attempt 1/3 | progress=7/432 (1.62%)
[2026-03-17T19:16:05] [INFO] [week_ranges] llm_success | duration=6.80s | cum_llm=49.59s | progress=7/432 (1.62%)
Hierarchy generation:   2%|▊                                             | 8/432 [00:53<46:16,  6.55s/step, year=2025 month=1 weeks=4][2026-03-17T19:16:05] [INFO] [week_ranges] step_done | year=2025 month=1 weeks=4 | progress=8/432 (1.85%)
[2026-03-17T19:16:05] [INFO] [day_ranges] stage_start | year=2025 month=1 week_bucket=1 days=[1, 2, 3, 4, 5, 6, 7, 8] | progress=8/432 (1.85%)
[2026-03-17T19:16:05] [INFO] [day_ranges] llm_attempt | attempt 1/3 | progress=8/432 (1.85%)
[2026-03-17T19:16:12] [INFO] [day_ranges] llm_success | duration=6.90s | cum_llm=56.50s | progress=8/432 (1.85%)
Hierarchy generation:   2%|▋                                | 9/432 [01:00<46:56,  6.66s/step, year=2025 month=1 week_bucket=1 days=8][2026-03-17T19:16:12] [INFO] [day_ranges] step_done | year=2025 month=1 week_bucket=1 days=8 | progress=9/432 (2.08%)
[2026-03-17T19:16:12] [INFO] [day_ranges] stage_start | year=2025 month=1 week_bucket=2 days=[9, 10, 11, 12, 13, 14, 15, 16] | progress=9/432 (2.08%)
[2026-03-17T19:16:12] [INFO] [day_ranges] llm_attempt | attempt 1/3 | progress=9/432 (2.08%)
[2026-03-17T19:16:18] [INFO] [day_ranges] llm_success | duration=5.40s | cum_llm=61.89s | progress=9/432 (2.08%)
Hierarchy generation:   2%|▋                               | 10/432 [01:05<44:05,  6.27s/step, year=2025 month=1 week_bucket=2 days=8][2026-03-17T19:16:18] [INFO] [day_ranges] step_done | year=2025 month=1 week_bucket=2 days=8 | progress=10/432 (2.31%)
[2026-03-17T19:16:18] [INFO] [day_ranges] stage_start | year=2025 month=1 week_bucket=3 days=[17, 18, 19, 20, 21, 22, 23, 24] | progress=10/432 (2.31%)
[2026-03-17T19:16:18] [INFO] [day_ranges] llm_attempt | attempt 1/3 | progress=10/432 (2.31%)
[2026-03-17T19:16:26] [INFO] [day_ranges] llm_success | duration=8.15s | cum_llm=70.05s | progress=10/432 (2.31%)
Hierarchy generation:   3%|▊                               | 11/432 [01:13<48:02,  6.85s/step, year=2025 month=1 week_bucket=3 days=8][2026-03-17T19:16:26] [INFO] [day_ranges] step_done | year=2025 month=1 week_bucket=3 days=8 | progress=11/432 (2.55%)
[2026-03-17T19:16:26] [INFO] [day_ranges] stage_start | year=2025 month=1 week_bucket=4 days=[25, 26, 27, 28, 29, 30, 31] | progress=11/432 (2.55%)
[2026-03-17T19:16:26] [INFO] [day_ranges] llm_attempt | attempt 1/3 | progress=11/432 (2.55%)
[2026-03-17T19:16:33] [INFO] [day_ranges] llm_success | duration=6.73s | cum_llm=76.78s | progress=11/432 (2.55%)
Hierarchy generation:   3%|▉                               | 12/432 [01:20<47:40,  6.81s/step, year=2025 month=1 week_bucket=4 days=7][2026-03-17T19:16:33] [INFO] [day_ranges] step_done | year=2025 month=1 week_bucket=4 days=7 | progress=12/432 (2.78%)
[2026-03-17T19:16:33] [INFO] [day_night_ranges] stage_start | date=2025-01-01 | progress=12/432 (2.78%)
[2026-03-17T19:16:33] [INFO] [day_night_ranges] llm_attempt | attempt 1/3 | progress=12/432 (2.78%)
[2026-03-17T19:16:37] [INFO] [day_night_ranges] llm_success | duration=4.48s | cum_llm=81.26s | progress=12/432 (2.78%)
Hierarchy generation:   3%|█▋                                                     | 13/432 [01:24<42:38,  6.11s/step, date=2025-01-01][2026-03-17T19:16:37] [INFO] [day_night_ranges] step_done | date=2025-01-01 | progress=13/432 (3.01%)
```
Here, as one can see, the idea is that the cyclical nature of the process goes through `year_ranges`, `season_ranges`, `month_ranges`, `day_ranges`, `day_night_ranges` -- covering different levels of variation over the course of a year. The generation process is therefore conditioned on the throughput of the `ollama` instance (in this example, ran with the help of an `NVIDIA RTX A6000`, a `step` (range estimation) takes roughly 6 seconds (but this can vary of course on your machine/hardware available).
