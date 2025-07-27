# predict.py
import os
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from utils import create_data_generators

def predict_image(model_path='model/pneumonia_model.h5', image_path=None, data_dir='data'):
    """Predict on a single image or test set."""
    model = load_model(model_path)
    
    if image_path:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image at {image_path}")
        img = cv2.resize(img, (224, 224))
        img = img / 255.0
        img = np.expand_dims(img, axis=0)
        
        prediction = model.predict(img)[0][0]
        return 'Pneumonia' if prediction > 0.5 else 'Normal', prediction
    
    else:
        _, _, test_generator = create_data_generators(data_dir)
        predictions = model.predict(test_generator)
        predicted_classes = ['Pneumonia' if pred > 0.5 else 'Normal' for pred in predictions]
        return predicted_classes

if __name__ == "__main__":
    try:
        result, confidence = predict_image(image_path='data/test/NORMAL/sample_image.jpg')
        print(f"Prediction: {result} (Confidence: {confidence:.4f})")
    except ValueError as e:
        print(f"Error: {e}")