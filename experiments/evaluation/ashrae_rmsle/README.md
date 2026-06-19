## Information about how data was obtained (for baselines and `aleth`)
You will find the for the experiment (the synthetic telemetry) under `data/functional`, and the real BGDP2 energy telemetry can be found under archive_files (make sure to expand it -- see instructions below). For how the synthetic data was obtained, we provide details below (for reproducibility):
1. `aleth`: for the `data/functional/synth_aleth` telemetry, we prompted `aleth` with ranges (known before-hand from the metadata information from each of the considered BGDP2 buildings in the experiment -- the ranges in this file `building_min_max_real_buildings_bgdp2.csv`). Specifically, we used the following script to generate the points (the prompt itself can be found at the `scenario=...` line:
```
set -euo pipefail

CSV_FILE="building_min_max_real_buildings_bgdp2.csv"
DELAY_SECONDS=$((220 * 60))   # 1h15m = 4500 seconds

tail -n +2 "$CSV_FILE" | while IFS=, read -r building_id min_meter_reading max_meter_reading; do

    building_id=$(echo "$building_id" | xargs)
    min_meter_reading=$(echo "$min_meter_reading" | xargs)
    max_meter_reading=$(echo "$max_meter_reading" | xargs)

    log_file="output_building${building_id}.log"
    scenario="Energy metering for a sensor between ${min_meter_reading} and ${max_meter_reading} kWh"

    echo "[$(date)] Launching building ${building_id}"
    echo "Scenario: $scenario"
    echo "Log: $log_file"

    nohup aleth --scenario "$scenario" --progress > "$log_file" 2>&1 &

    echo "[$(date)] Started PID $!"
    echo "Sleeping for ${DELAY_SECONDS} seconds..."
    sleep "$DELAY_SECONDS"
done

# nohup ./launch_aleth.sh > launcher.log 2>&1 &
```
This was to automate the collection of measurements from `aleth` (we added the logs for the execution under `data/functional/synth_aleth/logs` -- latencies may differ from reported performance in the paper, as some of the runs were concurrently deployed).

2. `synth_basic`: here, we used the script found under `data/functional/synth_basic/generate_building_scripts.py` to prompt models for code (again within bounds from BGDP2 buildings metadata -- subsequently, we parse the responses and save them separately, and ultimately run `data/functional/synth_basic/run_generated_scripts.py` to actually generate the csv data points (used in the evaluation).
3. `synth_prompted`: similarly to the point above, we used the script found under `data/functional/synth_prompted/generate_building_scripts.py` to prompt models for code (again within bounds from BGDP2 buildings metadata -- subsequently, we parse the responses and save them separately, and ultimately run `data/functional/synth_prompted/run_generated_scripts.py` to actually generate the csv data points used in the evaluation). The only diffence here is that the model is also explicitely asked to make the data as realistic as possible.
4. `random`: we used the script found under `data/functional/synth_prompted/generate_random_data_within_bounds.py` to generate the points for random data (again within bounds from BGDP2 buildings metadata). The random variable is uniformly samples between the bounds to produce hourly samples.


## Reproduce experiment
To reproduce results for the ASHRAE evaluation, you have to:
1. Expand the data (run the `rebuild_data_files.sh` file under data; ensure it is executable first by running `chmod +x rebuild_data_files.sh`)
2. Create venv and install dependencies (`python3 -m venv env`, activate it with `source env/bin/activate`and install requirements with `pip install -r requirements.txt`)
3. Run evaluation file with:
```
python evaluation.py \
  --data-dir . \
  --building-file buildings_considered.csv \
  --n-buildings 15 \
  --outdir evaluation_results \
  --random-dir functional/random
```
After successful completion (it should take roughly about 1 minute -- we ran the experiment on an AMD EPYC 9354P CPU with 32 cores), you should obtain the following table:
```
   Training signal  RMSLE Relative to real (%)
        Real BGDP2 0.2714                   --
   Aleth synthetic 1.6697              +515.3%
  Random synthetic 1.7090              +529.8%
Synthetic baseline 3.3869             +1148.0%
Prompted synthetic 3.7674             +1288.3%
```
Additionally, you should also see the results across buildings:
```
Per-building results:
 building_id    training_signal  rmsle relative_to_real_pct
          63         Real BGDP2 0.1289                   --
          90         Real BGDP2 0.0693                   --
          96         Real BGDP2 0.8501                   --
         110         Real BGDP2 0.0487                   --
         118         Real BGDP2 0.0656                   --
         122         Real BGDP2 0.0471                   --
         141         Real BGDP2 0.1027                   --
         177         Real BGDP2 0.2260                   --
         186         Real BGDP2 0.1855                   --
         204         Real BGDP2 0.0744                   --
         231         Real BGDP2 0.2173                   --
         232         Real BGDP2 0.0771                   --
         252         Real BGDP2 0.1664                   --
          63    Aleth synthetic 3.0312             +2251.6%
          90    Aleth synthetic 3.2711             +4621.9%
          96    Aleth synthetic 3.4173              +302.0%
         110    Aleth synthetic 0.2438              +400.5%
         118    Aleth synthetic 0.4383              +568.5%
         122    Aleth synthetic 0.1890              +301.3%
         141    Aleth synthetic 0.3185              +210.1%
         177    Aleth synthetic 1.4386              +536.4%
         186    Aleth synthetic 0.4836              +160.7%
         204    Aleth synthetic 0.2126              +185.7%
         231    Aleth synthetic 0.8044              +270.2%
         232    Aleth synthetic 0.2013              +161.1%
         252    Aleth synthetic 0.6961              +318.4%
          63 Synthetic baseline 4.2123             +3167.9%
          90 Synthetic baseline 4.5355             +6447.1%
          96 Synthetic baseline 4.8710              +473.0%
         110 Synthetic baseline 0.2104              +331.9%
         118 Synthetic baseline 5.7664             +8695.3%
         122 Synthetic baseline 5.6005            +11791.5%
         141 Synthetic baseline 0.2941              +186.3%
         177 Synthetic baseline 1.4833              +556.2%
         186 Synthetic baseline 0.5449              +193.8%
         204 Synthetic baseline 0.2116              +184.4%
         231 Synthetic baseline 4.2603             +1860.8%
         232 Synthetic baseline 0.2192              +184.3%
         252 Synthetic baseline 0.6792              +308.2%
          63 Prompted synthetic 4.2127             +3168.3%
          90 Prompted synthetic 3.3568             +4745.7%
          96 Prompted synthetic 4.8693              +472.8%
         110 Prompted synthetic 5.6874            +11577.6%
         118 Prompted synthetic 5.7659             +8694.5%
         122 Prompted synthetic 5.6005            +11791.5%
         141 Prompted synthetic 0.3497              +240.5%
         177 Prompted synthetic 5.6303             +2390.9%
         186 Prompted synthetic 0.5522              +197.7%
         204 Prompted synthetic 0.2224              +198.9%
         231 Prompted synthetic 0.7808              +259.4%
         232 Prompted synthetic 0.2424              +214.5%
         252 Prompted synthetic 0.6791              +308.2%
          63   Random synthetic 3.1148             +2316.5%
          90   Random synthetic 3.3547             +4742.7%
          96   Random synthetic 3.5076              +312.6%
         110   Random synthetic 0.1617              +232.0%
         118   Random synthetic 0.4325              +559.7%
         122   Random synthetic 0.1697              +260.3%
         141   Random synthetic 0.3071              +199.0%
         177   Random synthetic 1.4658              +548.5%
         186   Random synthetic 0.5198              +180.2%
         204   Random synthetic 0.1646              +121.2%
         231   Random synthetic 0.7743              +256.4%
         232   Random synthetic 0.1849              +139.8%
         252   Random synthetic 0.6965              +318.6%
```
