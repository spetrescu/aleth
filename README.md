# <img width="200" alt="aleth_logo" src="https://github.com/user-attachments/assets/0b89d8df-3601-40a1-9745-45974da18ea2" /> <br>
`aleth` was born out of a research innitiative to lower the barrier to synthetic sensor telemetry in buildings.

## Usage
`aleth` runs on top of [ollama](https://ollama.com) for local inference. Start the server with an extended context window before running anything:

```bash
OLLAMA_CONTEXT_LENGTH=64000 ollama serve &
ollama pull gpt-oss:20b
```

Install the package from `src/aleth/`, then point it at a scenario in plain English:

```bash
cd src/aleth && pip install -e .

aleth --scenario "CO2 sensor in a university lecture hall, heavy occupancy on weekdays" \
      --start-year 2024 --years 2 --freq-minutes 30
```

Each run writes a timestamped folder under `results/` with a CSV of the generated timeseries, a JSON of the inferred value ranges, and a set of diagnostic plots. The model and ollama endpoint can be changed in `config.py`.

```bash
# a few more examples of what the scenario argument can express
aleth --scenario "Temperature sensor on a rooftop HVAC unit in Madrid"
aleth --scenario "Water conductivity sensor in a building's cooling tower"
aleth --scenario "PM10 air quality sensor near a busy urban road, rush-hour spikes"
```

## Citation
To cite this work, feel free to use the following BibTeX entry:
```python
@inproceedings{petrescu2026aleth, 
  title={Generative Models as a Catalyst for Lowering the Barrier to Synthetic Sensor Telemetry},
  author={Petrescu, Stefan and Rellermeyer, Jan S.},
  year={2026},
  booktitle = {Proceedings of the 13th ACM International Conference on Systems for Energy-Efficient Buildings, Cities, and Transportation},
  series = {BuildSys '26}
}
```

