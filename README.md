# 🌍 RiskAtlas

RiskAtlas is a data-driven tool designed to assess country-level risks for market entry and industry implementation.

## 🚀 Features

- Load and process multiple Excel datasets
- Harmonize country names with GeoJSON standards
- Compute risk scores
- Visualize results on an interactive world map (Folium)

## 📁 Project Structure

- `src/` → core logic
- `data/` → datasets (not included)
- `outputs/` → generated maps

## ⚠️ Data

Raw datasets are not included due to confidentiality.

You can:
- use your own data
- or rely on the sample dataset in `data/sample/`

## 🛠️ Installation

```bash
# Navigate to the project directory (not the file)
cd YOUR_OWN_PATH/RiskAtlas

# Create a new conda environment with a specific Python version
conda create -n RiskAtlas python=3.11

# Activate the environment
conda activate RiskAtlas

# Install required Python dependencies
pip install -r requirements.txt