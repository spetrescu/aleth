# reproducibility
Before running any code, make sure you have extracted the data (you have to run bash scripts - see instructions under the `data` dir)

## Create venv
Assuming you have `venv` installed, first create a virtual environment to install dependencies required to run code. Therefore:
1.  Run `python3 -m venv env`
2. Run `source env/bin/activate`
3. Lastly, run `pip install -r requirements.txt`

## Prerequisite - serve `ollama`
Across experiments that use LLMs, we used `ollama` for serving the models. There are two main things you have to ensure regarding `ollama`, namely that the ollama server is running with the right configuration and that the model you are trying to run is actually downloaded on the machine. 

1. For the former (serving ollama), after you have installed `ollama` ([https://ollama.com/download/linux](https://ollama.com/download/linux)), make sure you run it with the following command: `OLLAMA_CONTEXT_LENGTH=64000 ollama serve &`. This ensure that the model runs with 64k as context instead of the default 2048.

2. For the latter (downloading models), assuming you have successfully managed to serve ollama, to download models of your choice simply run: `ollama pull <model>`, for example: `ollama pull gpt-oss:20b`.

After you have followed the two steps above, you should be setup for success with interfacing with ollama in order to reproduce experiments that use LLMs.

## 2a_figure.py
Assuming the virtual environment is activated and requirements have been installed, run: `python 2a_figure.py`
