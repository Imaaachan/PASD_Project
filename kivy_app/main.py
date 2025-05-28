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

API_KEY = "c8d3296b62fff12fbb62fd968f7812e3"

class WeatherApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.city_input = TextInput(hint_text="Masukkan nama kota", multiline=False, size_hint_y=None, height=50)
        self.result_label = Label(text="", size_hint_y=None, height=50)

        check_button = Button(text="Cek Cuaca", on_press=self.cek_cuaca, size_hint_y=None, height=50)

        self.layout.add_widget(self.city_input)
        self.layout.add_widget(check_button)
        self.layout.add_widget(self.result_label)

        return self.layout

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

    def cek_cuaca(self, instance):
        city = self.city_input.text
        lat, lon = self.get_coordinates(city)

        if lat is None or lon is None:
            self.result_label.text = "Kota tidak ditemukan :("
            return

        daily = self.get_weather_forecast(lat, lon)
        cuaca_hari_ini = daily[0]['weather'][0]['main']

        if 'Rain' in cuaca_hari_ini:
            hasil = "Hujan"
        else:
            hasil = "Tidak hujan"

        self.result_label.text = f"Hari ini di {city}: {hasil}"
    
    def buat_grafik_suhu(self, daily):
        suhu_harian = [day['temp']['day'] for day in daily[:7]]
        hari = list(range(1, 8))

        plt.clf()
        plt.plot(hari, suhu_harian, marker='o')
        plt.title('Suhu 7 Hari ke Depan')
        plt.xlabel('Hari')
        plt.ylabel('Suhu (°C)')
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        im = CoreImage(buf, ext='png')
        buf.close()

        if hasattr(self, 'grafik_suhu'):
            self.layout.remove_widget(self.grafik_suhu)

        self.grafik_suhu = Image(texture=im.texture, size_hint_y=None, height=300)
        self.layout.add_widget(self.grafik_suhu)

    def buat_grafik_kelembapan(self, daily):
        kelembapan = [day['humidity'] for day in daily[:7]]
        hari = list(range(1, 8))

        plt.clf()
        plt.plot(hari, kelembapan, marker='o', color='green')
        plt.title('Kelembapan 7 Hari ke Depan')
        plt.xlabel('Hari')
        plt.ylabel('Kelembapan (%)')
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        im = CoreImage(buf, ext='png')
        buf.close()

        if hasattr(self, 'grafik_kelembapan'):
            self.layout.remove_widget(self.grafik_kelembapan)

        self.grafik_kelembapan = Image(texture=im.texture, size_hint_y=None, height=300)
        self.layout.add_widget(self.grafik_kelembapan)
    
    def buat_grafik_tekanan(self, daily):
        tekanan = [day['pressure'] for day in daily[:7]]
        hari = list(range(1, 8))

        plt.clf()
        plt.plot(hari, tekanan, marker='o', color='orange')
        plt.title('Tekanan Udara 7 Hari ke Depan')
        plt.xlabel('Hari')
        plt.ylabel('Tekanan (hPa)')
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        im = CoreImage(buf, ext='png')
        buf.close()

        if hasattr(self, 'grafik_tekanan'):
            self.layout.remove_widget(self.grafik_tekanan)

        self.grafik_tekanan = Image(texture=im.texture, size_hint_y=None, height=300)
        self.layout.add_widget(self.grafik_tekanan)

if __name__ == '__main__':
    WeatherApp().run()
