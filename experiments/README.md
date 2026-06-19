# reproducibility
Before running any code, make sure you have extracted the data (you have to run bash scripts - see instructions under the `data` dir)

## Prerequisite
### Create venv
Assuming you have `venv` installed, first create a virtual environment to install dependencies required to run code. Therefore:
1.  Run `python3 -m venv env`
2. Run `source env/bin/activate`
3. Lastly, run `pip install -r requirements.txt`

### Prerequisite - serve `ollama`
Across experiments that use LLMs, we used `ollama` for serving the models. There are two main things you have to ensure regarding `ollama`, namely that the ollama server is running with the right configuration and that the model you are trying to run is actually downloaded on the machine. 

1. For the former (serving ollama), after you have installed `ollama` ([https://ollama.com/download/linux](https://ollama.com/download/linux)), make sure you run it with the following command: `OLLAMA_CONTEXT_LENGTH=64000 ollama serve &`. This ensure that the model runs with 64k as context instead of the default 2048.

2. For the latter (downloading models), assuming you have successfully managed to serve ollama, to download models of your choice simply run: `ollama pull <model>`, for example: `ollama pull gpt-oss:20b`.

After you have followed the two steps above, you should be setup for success with interfacing with ollama in order to reproduce experiments that use LLMs.

## Results
We provide the code for all the figures and tables, or any other claims made in the paper. Specifically, we separate the code for the figures and tables in the first part (before the results) from the results, to make it more easy to follow. We organize the rest therefore in three parts: (1) figures and tables, (2) results for off the shelf LLMs, (3) results for aleth.

### Figures and tables
All figure and table scripts are under `figures_and_tables/`. Run them from that directory with the venv activated.

#### Figure 1_figure.py
`python figures_and_tables/1_figure.py`

#### Figure 2a_figure.py
`python figures_and_tables/2a_figure.py`

#### Figure 2b_figure.py
`python figures_and_tables/2b_figure.py`

#### Figure 2c_figure.py
`python figures_and_tables/2c_figure.py`

#### Figure 4a_4b_figure.py
`python figures_and_tables/4a_4b_figure.py`

### Results 1/2 Off the shelf LLMs
Qualitative and quantitative results for the off-the-shelf LLM experiments are under `baselines/qualitative` and `baselines/quantitative`.

#### Table 4_table.py
`python figures_and_tables/4_table.py`

#### Figure 5a_5b_figure.py
This figure tests the data output capability of off-the-shelf LLMs. The generation script is `baselines/qualitative/5_test_data_volume_output_capability.py` (runs 1-31 days for 3 models). Pre-generated results are already provided in `baselines/qualitative/qualitative_results_incremental_by_no_days`. To plot directly:

`python figures_and_tables/5a_5b_figure.py`

#### Figure 6a_6b_6c_6d_figure.py
`python figures_and_tables/6a_6b_6c_6d_figure.py`

#### Figure 7a_7b_7c_7d_figure.py
`python figures_and_tables/7a_7b_7c_7d_figure.py`

#### Figure 8a_8b_figure.py
Models were prompted to generate OOB and Spikes anomalous regimes via `baselines/qualitative/8_prompt_for_anomalous_regimes.py`. The generated data is saved under `baselines/qualitative/ollama_results_anomalies_b113_round16`. To plot:

`python figures_and_tables/8a_8b_figure.py`

### Results 2/2 aleth
Functional evaluations for `aleth` are under `evaluation/`:
- `evaluation/ashrae_rmsle/` — ASHRAE energy metering RMSLE evaluation
- `evaluation/granger/` — Granger causality estimation experiment
