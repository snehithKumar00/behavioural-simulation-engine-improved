import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split

def train_churn_model(X_data, y_data):
    """
    Trains an LSTM model on the simulation telemetry.
    X_data shape: (samples, 30_days, 4_features)
    y_data shape: (samples,) binary 1 (churn) or 0 (survive)
    """
    # Split data into training and validation sets
    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2, random_state=42)

    # Construct the Deep Neural Network
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
        Dropout(0.2), # Regularization method
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid') # Binary classification output
    ])

    # Compile utilizing Adam optimizer
    model.compile(optimizer='adam', 
                  loss='binary_crossentropy', 
                  metrics=['accuracy'])

    print("Training LSTM Model...")
    history = model.fit(X_train, y_train, 
                        validation_data=(X_test, y_test),
                        epochs=20, 
                        batch_size=32)

    # Save the trained model for Flask to consume later
    model.save('churn_lstm_model.h5')
    print("Model saved to churn_lstm_model.h5")
    
    return model, history

if __name__ == '__main__':
    from engine import SimulationEngine
    
    # Generate a large dataset for training
    print("Generating simulation data...")
    config = {
        'num_players': 5000, # Large population to train the neural network
        'difficulty': 40,
        'difficulty_growth': 0.8,
        'reward_amount': 70,
        'penalty_on_failure': 1
    }
    
    engine = SimulationEngine(config)
    results = engine.run()
    
    print(f"Data generated. Extracted {len(results['X_tensor'])} valid player records.")
    train_churn_model(results['X_tensor'], results['y_tensor'])