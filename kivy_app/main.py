from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from joblib import load
import numpy as np
import pandas as pd
import os
import random

class SplashScreen(Screen):
    pass

model_dir = "models_per_location_feature_selection\\models_per_location_feature_selection"
dataset_path = "data_clean.csv" 

class HomeScreen(Screen):
    location_input = ObjectProperty(None)
    output_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.df = pd.read_csv(dataset_path)
        except FileNotFoundError:
            self.df = pd.DataFrame()
            print("⚠️ Dataset tidak ditemukan.")

    def generate_random_input(self, selected_features):
        if self.df.empty:
            return np.array([[random.uniform(0, 1) for _ in selected_features]])

        # Pilih baris acak dari dataset
        sample_row = self.df.sample(1).reset_index(drop=True)

        try:
            # Gunakan hanya kolom yang benar-benar ada di selected_features
            selected = [col for col in selected_features if col in sample_row.columns]
            input_data = sample_row[selected].to_numpy()
            
            # Pastikan hasilnya sesuai panjang fitur yang diminta
            if input_data.shape[1] != len(selected_features):
                raise ValueError("Jumlah fitur tidak cocok dengan yang diminta model.")
        except:
            input_data = np.array([[random.uniform(0, 1) for _ in selected_features]])

        return input_data


    def predict_weather(self):
        self.output_label.text = ""
        self.ids.loading_label.text = "⏳ Memuat prediksi cuaca..."

        location = self.ids.location_input.text.strip().capitalize()

        try:
            model_temp = load(os.path.join(model_dir, f"model_temp_{location}.joblib"))
            model_hum = load(os.path.join(model_dir, f"model_hum_{location}.joblib"))
            model_pres = load(os.path.join(model_dir, f"model_pres_{location}.joblib"))
            model_rain = load(os.path.join(model_dir, f"model_rain_{location}.joblib"))
            scaler = load(os.path.join(model_dir, f"scaler_{location}.joblib"))
        except:
            self.ids.loading_label.text = ""
            self.output_label.text = "❌ Model tidak ditemukan untuk lokasi itu :("
            return

        # Ambil fitur yang dipakai oleh model suhu (semua model pakai fitur sama)
        selected_features = model_temp.feature_names_in_

        # Ambil input dari dataset asli
        input_data = self.generate_random_input(selected_features)
        scaled_input = scaler.transform(input_data)

        # Prediksi
        temp = model_temp.predict(scaled_input)[0]
        hum = model_hum.predict(scaled_input)[0]
        pres = model_pres.predict(scaled_input)[0]
        rain = model_rain.predict(scaled_input)[0]

        status_hujan = "🌧️ Hujan" if rain == 1 else "☀️ Tidak Hujan"

        self.output_label.text = f"""
📍 Lokasi: {location}
🌡️ Suhu: {temp:.2f} °C
💧 Kelembapan: {hum:.2f} %
🌬️ Tekanan: {pres:.2f} hPa
🌦️ Cuaca: {status_hujan}
"""
        self.ids.loading_label.text = ""

class WeatherApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(HomeScreen(name="home"))
        return sm

if __name__ == '__main__':
    WeatherApp().run()
