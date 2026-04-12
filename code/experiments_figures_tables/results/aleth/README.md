# aleth

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
