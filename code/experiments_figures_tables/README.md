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

#### Figure 1_figure.py
Assuming the virtual environment is activated and requirements have been installed, run: `python 1_figure.py`

#### Figure 2a_figure.py
Assuming the virtual environment is activated and requirements have been installed, run: `python 2a_figure.py`

#### Figure 2b_figure.py
Assuming the virtual environment is activated and requirements have been installed, run: `python 2b_figure.py`

#### Figure 2c_figure.py
Assuming the virtual environment is activated and requirements have been installed, run: `python 2c_figure.py`

#### Figure 4a_4b_figure.py
Assuming the virtual environment is activated and requirements have been installed, run: `python 4a_4b_figure.py`

### Results 1/2 Off the shelf LLMs
To match the presentation of the paper, we provide the qualitative and quantitative results for the off the shelf LLM experiments (`results/off_the_shelf_llms/qualitative` and `results/off_the_shelf_llms/quantitative`).

#### Figures 5a and 5b
This figure in the paper was one example of how we tested the sheer data ouptut capability of off-the-shelf LLMs. To do so, we ran: 
1. `results/off_the_shelf_llms/qualitative/test_data_volume_output_capability.py` (this will generate data for 1-31 days for 3 models; you can run this if you want to reproduce the data itself, however, given the time it takes, we already provide the results in output txt files which can be found in `buildsys_github_submissions/submission_76/code/experiments_figures_tables/results/off_the_shelf_llms/qualitative/qualitative_results_incremental_by_no_days`). Therefore, to plot the results directly and reproduce Figure 5a and 5b, run the command below.
2. `results/off_the_shelf_llms/qualitative/plot_output_capability_fig5a_5b.py` (this will reproduce the visualization in the paper - Figure 5a and Figure 5b)
### Results 2/2 aleth
