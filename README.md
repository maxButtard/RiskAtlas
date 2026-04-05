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
- `outputs/` → generated maps (not included)
- `docs/` → example of generated map

## ⚠️ Data

Raw datasets are not included due to confidentiality.

You can:
- use your own data
- or rely on the sample dataset available in `data/sample/`

example with population on the map:
👉 [View interactive map](https://maxButtard.github.io/RiskAtlas/map.html)

For professional inquiries related to:
- risk analysis for market entry
- industry implementation
- mobility risk assessment within countries  

please contact: **lucie.balmana@gmail.com** or **buttardmaxence2@icloud.com**

## 🛠️ Installation

```bash
# Navigate to the project directory
cd YOUR_OWN_PATH/RiskAtlas

# Create a new conda environment
conda create -n RiskAtlas python=3.11

# Activate the environment
conda activate RiskAtlas

# Install dependencies
pip install -r requirements.txt