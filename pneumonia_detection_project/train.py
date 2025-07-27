# train.py
import os
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from utils import create_data_generators, build_cnn_model, plot_training_history, evaluate_model

def train_model(data_dir='data', model_save_path='model/pneumonia_model.h5'):
    """Train the CNN model and save the best weights."""
    # Create data generators
    train_generator, val_generator, test_generator = create_data_generators(data_dir)
    
    # Build model
    model = build_cnn_model()
    
    # Callbacks
    callbacks = [
        EarlyStopping(patience=10, restore_best_weights=True, monitor='val_accuracy'),
        ModelCheckpoint(model_save_path, save_best_only=True, monitor='val_accuracy'),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.00001)
    ]
    
    # Train model
    history = model.fit(
        train_generator,
        epochs=30,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate model
    evaluate_model(model, test_generator)
    
    # Plot training history
    plot_training_history(history)
    
    return model

if __name__ == "__main__":
    os.makedirs('model', exist_ok=True)
    train_model()