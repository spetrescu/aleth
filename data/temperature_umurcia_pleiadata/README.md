## Temperature dataset used

According to the official Zenodo resource (https://zenodo.org/records/7620136):
"This dataset presents detailed building operation data from the three blocks (A, B and C) of the Pleiades building of the University of Murcia, which is a pilot building of the European project PHOENIX. The aim of PHOENIX is to improve buildings efficiency, and therefore we included information of: (i) consumption data, aggregated by block in kWh; (ii) HVAC (Heating, Ventilation and Air Conditioning) data with several features, such as state (ON=1, OFF=0), operation mode (None=0, Heating=1, Cooling=2), setpoint and device type; (iii) indoor temperature  per room; (iv) weather data, including temperature, humidity, radiation, dew point, wind direction and precipitation; (v) carbon dioxide and presence data for few rooms; (vi) relationships between HVAC, temperature, carbon dioxide and presence sensors identifiers with their respective rooms and blocks. Weather data was acquired from the IMIDA (Instituto Murciano de Investigación y Desarrollo Agrario y Alimentario)."

## Reconstructing the dataset
The dataset is stored as split archive parts under `archive_files/` due to GitHub’s 100MB file limit.
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