from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import matplotlib.pyplot as plt
import io
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import numpy as np

import requests

from config import API_KEY

API = API_KEY

class SplashScreen(Screen):
    pass

class HomeScreen(Screen):
    def show_weather(self):
        city = self.ids.city_input.text
        lat, lon = self.get_coordinates(city)

        if lat is None or lon is None:
            self.ids.weather_label.text = "Kota tidak ditemukan :("
            return

        daily = self.get_weather_forecast(lat, lon)
        cuaca_hari_ini = daily[0]['weather'][0]['main']

        hasil = "Hujan" if 'Rain' in cuaca_hari_ini else "Tidak hujan"
        self.ids.weather_label.text = f"Hari ini di {city}: {hasil}"

        self.ids.chart_layout.clear_widgets()
        self.tampilkan_grafik(daily)

    def predict_weather(self):
        city = self.ids.city_input.text
        lat, lon = self.get_coordinates(city)

        if lat is None or lon is None:
            self.ids.prediction_label.text = "Kota tidak ditemukan :(" 
            return

        daily = self.get_weather_forecast(lat, lon)
        cuaca_besok = daily[1]['weather'][0]['main']

        hasil = "Hujan" if 'Rain' in cuaca_besok else "Tidak hujan"
        self.ids.prediction_label.text = f"Besok di {city}: {hasil}"

    def get_coordinates(self, city):
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        return None, None

    def get_weather_forecast(self, lat, lon):
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"
        response = requests.get(url)
        data = response.json()
        return data['daily']

    def tampilkan_grafik(self, daily):
        self.plot_data(
            [day['temp']['day'] for day in daily[:7]],
            'Suhu 7 Hari ke Depan',
            'Hari', 'Suhu (°C)'
        )
        self.plot_data(
            [day['humidity'] for day in daily[:7]],
            'Kelembapan 7 Hari ke Depan',
            'Hari', 'Kelembapan (%)',
            color='green'
        )
        self.plot_data(
            [day['pressure'] for day in daily[:7]],
            'Tekanan 7 Hari ke Depan',
            'Hari', 'Tekanan (hPa)',
            color='red'
        )

    def plot_data(self, values, title, xlabel, ylabel, color='blue'):
        hari = list(range(1, 8))

        plt.clf()
        plt.plot(hari, values, marker='o', color=color)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = CoreImage(buf, ext='png')
        buf.close()

        self.ids.chart_layout.add_widget(Image(texture=im.texture, size_hint_y=None, height=300))

class WeatherApp(App):
    def build(self):
        return ScreenManager()