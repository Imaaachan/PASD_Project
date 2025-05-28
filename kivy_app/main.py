from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage

import matplotlib.pyplot as plt
import io
import requests

from config import API_KEY

class WeatherApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Input kota dan tombol
        self.city_input = TextInput(hint_text="Masukkan nama kota", multiline=False, size_hint_y=None, height=40)
        check_button = Button(text="Cek Cuaca", size_hint_y=None, height=40)
        check_button.bind(on_press=self.cek_cuaca)

        # Label hasil cuaca
        self.result_label = Label(text="", size_hint_y=None, height=40)

        # Layout untuk grafik, dimasukkan dalam ScrollView
        self.graph_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.graph_layout.bind(minimum_height=self.graph_layout.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.graph_layout)

        # Tambahkan widget ke root layout
        root.add_widget(self.city_input)
        root.add_widget(check_button)
        root.add_widget(self.result_label)
        root.add_widget(scroll)

        return root

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
        city = self.city_input.text.strip()
        if not city:
            self.result_label.text = "Masukkan nama kota terlebih dahulu."
            return

        lat, lon = self.get_coordinates(city)
        if lat is None or lon is None:
            self.result_label.text = "Kota tidak ditemukan :("
            self.clear_graphics()
            return

        daily = self.get_weather_forecast(lat, lon)
        cuaca_hari_ini = daily[0]['weather'][0]['main']

        hasil = "Hujan" if 'Rain' in cuaca_hari_ini else "Tidak hujan"
        self.result_label.text = f"Hari ini di {city}: {hasil}"

        # Update grafik suhu, kelembapan, tekanan
        self.clear_graphics()
        self.buat_grafik_suhu(daily)
        self.buat_grafik_kelembapan(daily)
        self.buat_grafik_tekanan(daily)

    def clear_graphics(self):
        self.graph_layout.clear_widgets()

    def buat_grafik_suhu(self, daily):
        suhu_harian = [day['temp']['day'] for day in daily[:7]]
        hari = list(range(1, 8))

        plt.clf()
        plt.plot(hari, suhu_harian, marker='o')
        plt.title('Suhu 7 Hari ke Depan')
        plt.xlabel('Hari')
        plt.ylabel('Suhu (°C)')
        plt.grid(True)

        self.tampilkan_grafik()

    def buat_grafik_kelembapan(self, daily):
        kelembapan = [day['humidity'] for day in daily[:7]]
        hari = list(range(1, 8))

        plt.clf()
        plt.plot(hari, kelembapan, marker='o', color='green')
        plt.title('Kelembapan 7 Hari ke Depan')
        plt.xlabel('Hari')
        plt.ylabel('Kelembapan (%)')
        plt.grid(True)

        self.tampilkan_grafik()

    def buat_grafik_tekanan(self, daily):
        tekanan = [day['pressure'] for day in daily[:7]]
        hari = list(range(1, 8))

        plt.clf()
        plt.plot(hari, tekanan, marker='o', color='orange')
        plt.title('Tekanan Udara 7 Hari ke Depan')
        plt.xlabel('Hari')
        plt.ylabel('Tekanan (hPa)')
        plt.grid(True)

        self.tampilkan_grafik()

    def tampilkan_grafik(self):
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        im = CoreImage(buf, ext='png')
        buf.close()

        grafik = Image(texture=im.texture, size_hint_y=None, height=300)
        self.graph_layout.add_widget(grafik)

if __name__ == '__main__':
    WeatherApp().run()