# 基於 CNN 及 IR 影像重建即時 TC 四象限近地面風速資訊
### Reconstruction of Real-time TC Quadrant Surface Wind Field based on CNN and IR Imagery

---

## Project Overview
Due to the scarcity of in-situ meteorological observations over open oceans, estimating the intensity and structure of Tropical Cyclones (TC) remains a significant challenge. 

This project, led by **Chun-Po (Popo)**, proposes a deep learning-based framework to reconstruct real-time TC surface wind information. By leveraging Geostationary Infrared (IR) imagery and Convolutional Neural Networks (CNN), the system estimates wind speed distributions across the four quadrants (**NE, SE, SW, NW**), providing higher spatial resolution than traditional Dvorak techniques.

## Core Methodology
* **Data Source**: GOES-R Series CMI (Cloud and Moisture Imagery) products.
* **Image Processing**:
    * **Coordinate Transformation**: Converting Geostationary projection to Latitude/Longitude grids using `xarray` and `pyproj`.
    * **Quadrant-based Cropping**: A specialized preprocessing pipeline that extracts 400x400 km sub-images for each quadrant relative to the TC center to capture asymmetric wind field features.
    * Note: The WSProfile dataset is currently not available to publish here.
