# Import necessary libraries
import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
from art import text2art
import os
from dotenv import load_dotenv

class LotteryAi:
    data_dir = ''
    def __init__(self):
        # Initialize any variables you need here
        load_dotenv()
        self.data_dir = os.getenv('STORE_DIR')
        pass

    # Function to print the introduction of the program
    def print_intro(self, model_name):
        # Generate ASCII art with the text "LotteryAi"
        ascii_art = text2art(model_name)
        # Print the introduction and ASCII art
        print("============================================================")
        print("LotteryAi")
        print("============================================================")
        print(ascii_art)
        print("Lottery prediction artificial intelligence")

    # Function to load data from a file and preprocess it
    def load_data(self, model_name):
        # Load data from file, ignoring white spaces and accepting unlimited length numbers
        data = np.genfromtxt(self.data_dir + '/' + model_name + '.csv', delimiter=',', dtype=int)
        # Replace all -1 values with 0
        data[data == -1] = 0
        # Split data into training and validation sets
        train_data = data[:int(0.8*len(data))]
        val_data = data[int(0.8*len(data)):]
        # Get the maximum value in the data
        max_value = np.max(data)
        return train_data, val_data, max_value

    # Function to create the model
    def create_model(self, num_features, max_value):
        # Create a sequential model
        model = keras.Sequential()
        # Add an Embedding layer, LSTM layer, and Dense layer to the model
        model.add(layers.Embedding(input_dim=max_value+1, output_dim=64))
        model.add(layers.LSTM(256))
        model.add(layers.Dense(num_features, activation='softmax'))
        # Compile the model with categorical crossentropy loss, adam optimizer, and accuracy metric
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    # Function to train the model
    def train_model(self, model_name):
        
        # Load and preprocess data 
        train_data, val_data, max_value = self.load_data(model_name)
        
        # Get number of features from training data 
        num_features = train_data.shape[1]

        # Create and compile model 
        model = self.create_model(num_features, max_value)

        # Fit the model on the training data and validate on the validation data for 100 epochs
        history = model.fit(train_data, train_data, validation_data=(val_data, val_data), epochs=100)

        # Delete the previous model file
        model_file = f'./models/{model_name}.keras'
        try:
            os.remove(model_file)
        except FileNotFoundError:
            pass

        # Save the model to a file
        model.save(model_file)

        # Get the validation accuracy from the history
        val_accuracy = history.history['val_accuracy'][-1]
        with open(f'./models/{model_name}_val_accuracy.txt', 'w') as f:
            f.write(str(val_accuracy))


    # Function to predict numbers using the trained model
    def predict_numbers(self, model, val_data, num_features):
        # Predict on the validation data using the model
        predictions = model.predict(val_data)
        # Get the indices of the top 'num_features' predictions for each sample in validation data
        indices = np.argsort(predictions, axis=1)[:, -num_features:]
        # Get the predicted numbers using these indices from validation data
        predicted_numbers = np.take_along_axis(val_data, indices, axis=1)
        return predicted_numbers

    # Function to print the predicted numbers
    def print_predicted_numbers(self, predicted_numbers):
        # Print a separator line and "Predicted Numbers:"
        print("============================================================")
        print("Predicted Numbers:")
        # Print only the first row of predicted numbers
        print(', '.join(map(str, predicted_numbers[0])))
        print("============================================================")

    # Main function to run everything   
    def train(self, model_name):
        # Print introduction of program 
        self.print_intro(model_name)

        # Train model 
        self.train_model(model_name)

    # Main function to run everything   
    def predict(self, model_name, number_of_future=None):
        # Load and preprocess data 
        train_data, val_data, max_value = self.load_data(model_name)
        
        # Get number of features from training data, if number_of_future is not None and not vietlot-655, use it
        print(model_name, number_of_future)
        if number_of_future and 'vietlot-655'.__ne__(model_name):
            num_features = number_of_future
        else:
            num_features = train_data.shape[1]

        # Load the model from a file
        model_file = f'./models/{model_name}.keras'
        model = keras.models.load_model(model_file)

        # Predict numbers using trained model 
        predicted_numbers = self.predict_numbers(model, val_data, num_features)
        # check val_accurarcy file exist, if not, return empty list
        val_accuracy_file = f'./models/{model_name}_val_accuracy.txt'
        if not os.path.exists(val_accuracy_file):
            val_accuracy = 0
        else:
            with open(val_accuracy_file, 'r') as f:
                val_accuracy = float(f.read())

        results = [f"{num}({val_accuracy*100:.0f}%)" for num in predicted_numbers[0]]

        return results