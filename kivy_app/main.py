from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
import matplotlib.pyplot as plt
import io
import requests

from config import API_KEY

class WeatherRoot(BoxLayout):
    pass

class WeatherApp(App):
    def build(self):
        return WeatherRoot()

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

    def cek_cuaca(self, *args):
        root = self.root
        city = root.city_input.text.strip()
        if not city:
            root.result_label.text = "Masukkan nama kota terlebih dahulu."
            self.clear_graphics()
            return

        lat, lon = self.get_coordinates(city)
        if lat is None or lon is None:
            root.result_label.text = "Kota tidak ditemukan :("
            self.clear_graphics()
            return

        daily = self.get_weather_forecast(lat, lon)
        cuaca_hari_ini = daily[0]['weather'][0]['main']

        hasil = "Hujan" if 'Rain' in cuaca_hari_ini else "Tidak hujan"
        root.result_label.text = f"Hari ini di {city}: {hasil}"

        self.clear_graphics()
        self.buat_grafik_suhu(daily)
        self.buat_grafik_kelembapan(daily)
        self.buat_grafik_tekanan(daily)

    def clear_graphics(self):
        self.root.graph_layout.clear_widgets()

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
        self.root.graph_layout.add_widget(grafik)

if __name__ == '__main__':
    WeatherApp().run()
