# sentinel1-radar-case-study
Second case study on sentinel-1 radar

**Radar Sentinel-1 Preprocessing & Visualization Toolkit**

Radar_cs is a Python package which provides tools for preprocessing Sentinel-1 Synthetic Aperture Radar (SAR) data and visualizing key radar backscatter components (VV, VH, VV/VH ratio). It uses the ESA SNAP `esa_snappy` interface and additional utilities to handle reprojection, rescaling, and image generation.

---

## ✨ Features

- ✅ Preprocess Sentinel-1 SLC data (Apply orbit, thermal noise removal, calibration, deburst, speckle filtering, terrain correction, AOI subset)
- ✅ Export processed outputs as BEAM-DIMAP and GeoTIFF
- ✅ Reproject GeoTIFF outputs to target CRS
- ✅ Visualize VV, VH, and VV/VH ratio with grayscale and RGB composite plots

---

## 🛠 Requirements

- Python 3.10
- SNAP (v10)
- [esa-snappy](https://step.esa.int/main/toolboxes/snap/)  
- numpy  
- matplotlib  
- rasterio  
- GDAL (for reprojection)

Make sure SNAP (Sentinel Application Platform) is installed and `esa_snappy` is configured correctly.

---

## 🚀 How to Run

```bash
python src/radar_cs/main.py
```

This will:

1. Load Sentinel-1 SLC product (expected as ZIP or SAFE)
2. Apply SNAP processing steps:
   - Apply orbit file
   - Remove thermal noise
   - Calibrate to Sigma0
   - Deburst IW bursts
   - Apply speckle filtering
   - Perform terrain correction
   - Subset to AOI defined in `AOI_Rubicon_sent1.geojson`
3. Save outputs to the `outputs/` folder
4. Reproject the generated GeoTIFF to the target CRS (e.g., EPSG:3857)
5. Generate visualization images:
   - VV grayscale (`*_vv.png`)
   - VH grayscale (`*_vh.png`)
   - RGB composite (`*_rgb.png`)

### 📥 User-Defined Inputs

The user needs to provide the following inputs before running the script:

- **Sentinel-1 product file**: A ZIP or SAFE file containing the Sentinel-1 SLC data, specified by the `file_path` variable in `main.py`.  
  Example: `data/S1A_IW_SLC__1SDV_20250503T173148_20250503T173215_059033_07527A_2B0C.SAFE.zip`

- **AOI GeoJSON file**: A GeoJSON file defining the Area of Interest (AOI) for subsetting, specified by the `aoi_geojson` parameter in the `preprocess_slc()` function.  
  Example: `AOI_Rubicon_sent1.geojson`

- **Target Coordinate Reference System (CRS)**: The desired projection for the final GeoTIFF output, defined by the `crs` variable in `main.py`.  
  Example: `'EPSG:3857'`

Make sure to update these paths and CRS settings in `main.py` to match your local data and desired output.

### ⏳ What Would I Have Done With More Time

If I had more time, I would have:

- **Created functions for each step**: Breaking down the preprocessing pipeline into smaller, modular functions for each operation would make the code more flexible and easier to maintain. This would allow users to call individual steps as needed rather than running the full pipeline.
  
- **Explored the individual processing steps more deeply**: I would dive deeper into each SNAP operator and process to understand their behavior in greater detail. This would allow me to determine the most appropriate operators for different use cases, optimizing the pipeline depending on the user's specific objectives.

- **Developed a user interface**: I would create a user-friendly interface, similar to SNAP, allowing users to interact with the pipeline more easily. This could include a graphical user interface (GUI) where users can select input files, choose processing steps, define outputs, and view results interactively without needing to modify the code directly. Streamlit would be a good choice for a rapid solution but there might be problems integrating snap and esa_snappy

### 📚 References

- [ESA SNAP (Sentinel Application Platform)](https://step.esa.int/main/toolboxes/snap/)  
  The official platform for processing and analyzing Sentinel-1, Sentinel-2, and other Earth Observation data.
- [Pyenv installation](https://github.com/pyenv/pyenv?tab=readme-ov-file)
- [Install python build dependencies] (https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
- [Tutorial to install and use snap with Python](https://senbox.atlassian.net/wiki/spaces/SNAP/pages/19300362/How+to+use+the+SNAP+API+from+Python)
- [Link to input example on copernicus hub](https://browser.dataspace.copernicus.eu/?zoom=8&lat=45.773&lng=7.33956&themeId=MONITORING&visualizationUrl=U2FsdGVkX1%2FzK44xhqmSHnCy4Qkufk1FyTJjW9Iug5QHc0VAr9oRwvAPl3%2BUcDhJlHDp9ZNB82SfLTQuAlQ7CR%2Fjtb6BLqCT5PE3f89mu7TbARPTkZKoz0%2FUydVdaiVo&datasetId=S2_L2A_CDAS)

- SLC Images processing documention :
   - https://www.earthdata.nasa.gov/s3fs-public/2024-06/SAR_DataProcessing_1page_new.pdf
   - Preprocessing https://www.ai4europe.eu/sites/default/files/2023-11/AI4Copernicus_S1SLCPreprocessing.pdf

