import os
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras.layers import LSTM, Dense, Dropout # type: ignore
from tensorflow.keras.models import Sequential, load_model # type: ignore

class DataLoader:
    """Класс для загрузки и хранения данных"""

    def __init__(self, file_path, features, targets):
        self.data = pd.read_csv(file_path)
        self.features = features
        self.targets = targets

    def get_features_and_targets(self):
        X = self.data[self.features].values
        Y = self.data[self.targets].values
        return X, Y

class Normalizer:
    """Класс для нормализации данных с помощью MinMaxScaler"""

    def __init__(self):
        self.scaler_X = MinMaxScaler()
        self.scaler_Y = MinMaxScaler()

    def fit_transform(self, X, Y):
        X_scaled = self.scaler_X.fit_transform(X)
        Y_scaled = self.scaler_Y.fit_transform(Y)
        return X_scaled, Y_scaled

    def transform(self, X, Y):
        X_scaled = self.scaler_X.transform(X)
        Y_scaled = self.scaler_Y.transform(Y)
        return X_scaled, Y_scaled

    def inverse_transform_X(self, X_scaled):
        return self.scaler_X.inverse_transform(X_scaled)

    def inverse_transform_Y(self, Y_scaled):
        return self.scaler_Y.inverse_transform(Y_scaled)

class DataProcessor:
    """Класс для разделения данных на тренировочные и тестовые выборки"""

    def __init__(self, test_size=0.2, random_state=50):
        self.test_size = test_size
        self.random_state = random_state

    def split_data(self, X, Y):
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=self.test_size, random_state=self.random_state)
        return X_train, X_test, Y_train, Y_test

class LSTMModelBuilder:
    """Класс для создания и конфигурации LSTM модели"""

    def __init__(self, input_shape):
        self.input_shape = input_shape

    # Лучший результат ошибки: loss: 0.0051, val_loss: 0.0012
    # Это абсолютный рекорд для обучения на реальных данных

    # Лучший результат ошибки: loss: 0.0041, val_loss: 0.0012
    # Это абсолютный рекорд для обучения на синтетических данных (батч 256)
    def build_model(self):
        model = Sequential()
        # Большое кол-во нейронов и возможность возврата последовательностей
        model.add(LSTM(512, activation='tanh', input_shape=self.input_shape, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(256, activation='tanh', return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(128, activation='tanh', return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(5))
        optimizer = Adam(learning_rate=0.0005)
        model.compile(optimizer=optimizer, loss='huber')
        return model

    '''
    def build_model(self):
        model = Sequential()
        # Большое кол-во нейронов и возможность возврата последовательностей
        model.add(LSTM(512, activation='tanh', input_shape=self.input_shape, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(256, activation='tanh', return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(128, activation='tanh', return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(64, activation='tanh', return_sequences=False))
        model.add(Dropout(0.3))
        model.add(Dense(5))
        optimizer = Adam(learning_rate=0.0005)
        model.compile(optimizer=optimizer, loss='huber')
        return model'''

class DenseModelBuilder:
    """Класс для создания и конфигурации Dense модели для одиночных предсказаний"""

    def __init__(self, input_shape):
        self.input_shape = input_shape

    def build_model(self):
        model = Sequential()
        model.add(Dense(128, activation='relu', input_shape=self.input_shape))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(5))
        model.compile(optimizer='adam', loss='mse')
        return model

class Trainer:
    """Класс для обучения модели"""

    def __init__(self, model, X_train, Y_train, batch_size=32, epochs=15, validation_split=0.2):
        self.model = model
        self.X_train = X_train
        self.Y_train = Y_train
        self.batch_size = batch_size
        self.epochs = epochs
        self.validation_split = validation_split

    def train(self):
        self.model.fit(self.X_train, self.Y_train, batch_size=self.batch_size, epochs=self.epochs, validation_split=self.validation_split)

class SynthTrainer:
    """Класс для обучения модели"""

    def __init__(self, model, X_train, Y_train, batch_size=258, epochs=15, validation_split=0.2):
        self.model = model
        self.X_train = X_train
        self.Y_train = Y_train
        self.batch_size = batch_size
        self.epochs = epochs
        self.validation_split = validation_split

    def train(self):
        self.model.fit(self.X_train, self.Y_train, batch_size=self.batch_size, epochs=self.epochs, validation_split=self.validation_split)

class Predictor:
    """Класс для генерации предсказаний с помощью обученной модели"""

    def __init__(self, model, scaler_Y):
        self.model = model
        self.scaler_Y = scaler_Y

    def make_predictions(self, initial_input, steps):
        current_input = initial_input.reshape((1, 1, initial_input.shape[0]))
        predictions = []
        pred = self.model.predict(current_input)
        predictions.append(self.scaler_Y.inverse_transform(pred))

        for step in range(1, steps):
            current_input = np.concatenate([initial_input[:5], pred.flatten()]).reshape((1, 1, 10))
            pred = self.model.predict(current_input)
            predictions.append(self.scaler_Y.inverse_transform(pred))
        return np.array(predictions)

    def make_predictions2(self, initial_input, steps):
        current_input = initial_input.reshape((1, 1, initial_input.shape[1])) # shape[2]
        predictions = []
        pred = self.model.predict(current_input)
        predictions.append(self.scaler_Y.inverse_transform(pred))

        for step in range(1, steps):
            current_input = np.concatenate([initial_input.flatten()[:5], pred.flatten()]).reshape((1, 1, 10))
            pred = self.model.predict(current_input)
            predictions.append(self.scaler_Y.inverse_transform(pred))
        return np.array(predictions)

class ModelManager:
    """Класс для управления сохранением и загрузкой моделей"""

    @staticmethod
    def save_model(model, model_path):
        """Сохраняет модель по указанному пути"""
        model.save(model_path)
        print(f"Модель сохранена по пути: {model_path}")

    @staticmethod
    def load_model(model_path, custom_objects=None, compile_model=True):
        """Загружает модель с указанного пути"""
        if os.path.exists(model_path):
            model = load_model(model_path, custom_objects=custom_objects, compile=compile_model)
            print(f"Модель загружена из файла: {model_path}")
            return model
        else:
            print(f"Файл с моделью по пути {model_path} не найден.")
            return None
