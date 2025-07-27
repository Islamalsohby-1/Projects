# README.md
# Pneumonia Detection using CNN

This project trains a Convolutional Neural Network (CNN) to classify chest X-ray images as Normal or Pneumonia using the Kaggle Chest X-Ray Images (Pneumonia) dataset.

## Project Structure
pneumonia_detection_project/ ├── data/ │ ├── train/ │ │ ├── NORMAL/ │ │ └── PNEUMONIA/ │ ├── val/ │ │ ├── NORMAL/ │ │ └── PNEUMONIA/ │ ├── test/ │ │ ├── NORMAL/ │ │ └── PNEUMONIA/ ├── requirements.txt ├── train.py ├── predict.py ├── utils.py ├── model/ │ └── pneumonia_model.h5 ├── plots/ │ ├── training_plots.png └── README.md

Setup Instructions
1. **Dataset**:
   - Download the dataset from [Kaggle](https://www.kaggle.com/paultimothymooney/chest-xray-pneumonia).
   - Unzip and place it in the `data/` folder with the structure shown above.
   - Alternatively, create placeholder directories with a few sample images (e.g., 10 per class) for testing.

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt





