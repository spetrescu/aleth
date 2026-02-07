# Electrical metering dataset used
The dataset is from the publicly available resoource at [https://www.kaggle.com/datasets/claytonmiller/buildingdatagenomeproject2](https://www.kaggle.com/datasets/claytonmiller/buildingdatagenomeproject2)

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
Before running the bash script, make sure it is executable (you can run chmod +x rebuild_data_files.sh)
