import os
import datetime
import pandas as pd
import joblib # Digunakan untuk memuat model Scikit-learn (.pkl). Jika modelmu beda (TensorFlow, PyTorch), sesuaikan.
import numpy as np

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty

# Untuk grafik Matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

# Load the Kivy file (pastikan nama file .kv kamu adalah weather.kv)
Builder.load_file('weather.kv')

class WeatherRoot(BoxLayout):
    # Properti Kivy untuk diperbarui dari Python dan ditampilkan di KV
    weather_status = StringProperty("Memuat Prediksi...")
    temperature = StringProperty("--°C")
    pressure = StringProperty("-- hPa")
    humidity = StringProperty("--%")
    weather_icon_source = StringProperty('assets/icon/clouds.png') # Default icon jika belum ada data

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_model = None
        self.pressure_model = None
        self.humidity_model = None
        self.historical_data = pd.DataFrame()
        self.forecast_data = [] # List untuk menyimpan hasil prediksi 5 hari

        # Panggil fungsi untuk memuat model dan data saat aplikasi dimulai
        self.load_models()
        self.load_historical_weather_data()
        
        # Lakukan prediksi dan perbarui UI setelah semuanya siap
        self.make_and_display_forecast()
        
        # Gambar grafik setelah UI di-render (berikan sedikit delay agar semua komponen UI siap)
        Clock.schedule_once(self.draw_graphs, 1)

    def load_models(self):
        """Memuat model machine learning dari folder 'model/'."""
        try:
            # Sesuaikan path dan nama file modelmu
            # Contoh: temp_model.pkl, pressure_model.pkl, humidity_model.pkl
            self.temp_model = joblib.load('model/temp_model.pkl')
            self.pressure_model = joblib.load('model/pressure_model.pkl')
            self.humidity_model = joblib.load('model/humidity_model.pkl')
            print("Model berhasil dimuat.")
        except FileNotFoundError:
            print("Error: Satu atau lebih file model tidak ditemukan. Pastikan ada di folder 'model/' dan namanya benar.")
            self.weather_status = "Error: Model tidak ditemukan."
        except Exception as e:
            print(f"Error saat memuat model: {e}")
            self.weather_status = f"Error memuat model: {e}"

    def load_historical_weather_data(self, filepath='weatherAUS.csv'):
        """Memuat data historis dari CSV dan melakukan preprocessing."""
        try:
            df = pd.read_csv(filepath)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Urutkan berdasarkan tanggal dan drop duplikat jika ada, ambil entri terbaru
            # Ini penting agar kita mendapatkan data terbaru sebagai input untuk prediksi
            df = df.sort_values(by='Date').drop_duplicates(subset=['Date'], keep='last')
            
            # --- PENTING: SESUAIKAN DENGAN FITUR INPUT MODEL KAMU ---
            # Pilih kolom yang relevan sebagai fitur input untuk modelmu
            # Contoh: model memprediksi berdasarkan Temp3pm, Pressure3pm, Humidity3pm
            # Jika modelmu butuh fitur lain (misal: MinTemp, MaxTemp, WindGustSpeed, dll.),
            # tambahkan ke list ini dan pastikan kolomnya ada di CSV.
            required_cols_for_model = ['Date', 'Temp3pm', 'Pressure3pm', 'Humidity3pm']
            
            # Tambahkan juga 'RainTomorrow' jika kamu menggunakannya untuk logika ikon
            if 'RainTomorrow' not in required_cols_for_model:
                required_cols_for_model.append('RainTomorrow')

            # Hapus baris dengan NaN di kolom yang dibutuhkan model
            self.historical_data = df[required_cols_for_model].dropna()
            
            if self.historical_data.empty:
                raise ValueError("Data historis kosong setelah preprocessing. Cek kembali kolom yang dibutuhkan dan nilai NaN.")

            print(f"Data historis dimuat. Jumlah baris: {len(self.historical_data)}")

        except FileNotFoundError:
            print(f"Error: File '{filepath}' tidak ditemukan. Pastikan 'weatherAUS.csv' ada di root folder 'kivy_app'.")
            self.weather_status = "Dataset tidak ditemukan!"
        except KeyError as e:
            print(f"Error: Kolom yang diharapkan tidak ada: {e}. Pastikan 'weatherAUS.csv' memiliki kolom yang sesuai dengan fitur model.")
            self.weather_status = f"Kolom '{e}' tidak ditemukan di dataset!"
        except ValueError as e:
            print(f"Error: {e}")
            self.weather_status = f"Error data: {e}"
        except Exception as e:
            print(f"Error saat memuat data historis: {e}")
            self.weather_status = f"Error memuat data: {e}"

    def make_and_display_forecast(self):
        """Membuat prediksi 5 hari ke depan menggunakan model ML dan memperbarui UI."""
        if self.temp_model is None or self.pressure_model is None or self.humidity_model is None:
            self.weather_status = "Model belum dimuat. Tidak bisa membuat prediksi."
            return
        
        if self.historical_data.empty:
            self.weather_status = "Data kosong. Tidak bisa membuat prediksi."
            return

        # Ambil data hari terakhir dari historical_data sebagai input awal untuk prediksi
        # Ini akan menjadi "kondisi saat ini" untuk memulai rantai prediksi.
        last_day_data = self.historical_data.iloc[-1]
        
        # --- PENTING: SESUAIKAN DENGAN INPUT MODEL KAMU ---
        # Buat array fitur input yang sesuai dengan training data model kamu.
        # Misalnya, jika model dilatih dengan [Temp3pm, Pressure3pm, Humidity3pm], maka:
        current_features_input = np.array([[
            last_day_data['Temp3pm'],
            last_day_data['Pressure3pm'],
            last_day_data['Humidity3pm']
            # Tambahkan fitur lain di sini sesuai kebutuhan modelmu
        ]])
        
        self.forecast_data = [] # Reset data prakiraan
        current_date_for_forecast = last_day_data['Date'] # Mulai dari tanggal terakhir di dataset

        for i in range(5): # Prediksi untuk 5 hari ke depan
            try:
                # Lakukan prediksi menggunakan model
                predicted_temp = self.temp_model.predict(current_features_input)[0]
                predicted_pressure = self.pressure_model.predict(current_features_input)[0]
                predicted_humidity = self.humidity_model.predict(current_features_input)[0]
                
                # --- Logika untuk menentukan status hujan ---
                # Ini adalah asumsi sederhana. Idealnya kamu punya model klasifikasi hujan sendiri.
                is_raining = "Tidak Hujan"
                if predicted_humidity > 70 and predicted_temp < 25: # Contoh ambang batas
                     is_raining = "Hujan"

                # Hitung tanggal untuk hari prediksi ini
                forecast_date_obj = current_date_for_forecast + datetime.timedelta(days=i+1)
                
                self.forecast_data.append({
                    'date': forecast_date_obj.strftime('%a, %d %b'), # Contoh: Mon, 01 Jan
                    'temp': predicted_temp,
                    'pressure': predicted_pressure,
                    'humidity': predicted_humidity,
                    'rain_status': is_raining # Menyimpan status hujan untuk hari ini
                })
                
                # --- UPDATE current_features_input untuk prediksi hari berikutnya ---
                # Ini adalah bagian kunci dari multi-step forecasting:
                # Output prediksi hari ini menjadi input untuk prediksi hari berikutnya.
                current_features_input = np.array([[
                    predicted_temp,
                    predicted_pressure,
                    predicted_humidity
                    # Update fitur lain jika ada, dengan nilai prediksi atau asumsi
                ]])

            except Exception as e:
                print(f"Error saat prediksi hari ke-{i+1}: {e}")
                self.weather_status = f"Error prediksi: {e}"
                break # Hentikan loop jika ada error

        if self.forecast_data:
            # Tampilkan data prakiraan untuk "hari ini" (yaitu, hari pertama dari prediksi 5 hari)
            today_forecast = self.forecast_data[0]
            self.weather_status = f"Prediksi Hari Ini ({today_forecast['date']}): {today_forecast['rain_status']}"
            self.temperature = f"{today_forecast['temp']:.1f}°C"
            self.pressure = f"{today_forecast['pressure']:.1f} hPa"
            self.humidity = f"{today_forecast['humidity']:.1f}%"
            
            # Atur ikon berdasarkan status hujan hari ini
            if today_forecast['rain_status'] == "Hujan":
                self.weather_icon_source = 'assets/icon/rain.png'
            else:
                self.weather_icon_source = 'assets/icon/sun.png'
            
            self.draw_graphs() # Gambar grafik dengan data prakiraan yang baru
        else:
            self.weather_status = "Gagal membuat prediksi. Cek model dan data."

    def draw_graphs(self, *args):
        """Menggambar grafik suhu, tekanan, dan kelembapan untuk 5 hari ke depan."""
        self.ids.graph_container.clear_widgets() # Bersihkan widget grafik lama jika ada

        if not self.forecast_data:
            self.ids.graph_container.add_widget(Label(text="Tidak ada data prakiraan untuk grafik.", halign='center', valign='middle'))
            return

        # Ekstrak data untuk grafik
        dates = [d['date'] for d in self.forecast_data]
        temps = [d['temp'] for d in self.forecast_data]
        pressures = [d['pressure'] for d in self.forecast_data]
        humidities = [d['humidity'] for d in self.forecast_data]

        graph_titles = ["Suhu (°C)", "Tekanan (hPa)", "Kelembapan (%)"]
        graph_data = [temps, pressures, humidities]
        colors = ['red', 'blue', 'green']

        for i, (title, data, color) in enumerate(zip(graph_titles, graph_data, colors)):
            fig, ax = plt.subplots(figsize=(4, 2)) # Ukuran kecil untuk setiap grafik
            ax.plot(dates, data, marker='o', color=color)
            ax.set_title(title, fontsize=10) # Atur ukuran font judul
            ax.tick_params(axis='x', rotation=45, labelsize=8) # Rotasi dan ukuran font label X
            ax.tick_params(axis='y', labelsize=8) # Ukuran font label Y
            ax.grid(True, linestyle='--', alpha=0.7) # Tambah grid
            plt.tight_layout() # Sesuaikan layout agar tidak ada tumpang tindih

            # Render Matplotlib figure ke Kivy Texture
            canvas = fig.canvas
            canvas.draw()
            buf = fig.canvas.buffer_rgba()
            width, height = fig.canvas.get_width_height()

            texture = Texture.create(size=(width, height), colorfmt='rgba')
            texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
            
            # Buat Image widget dari texture dan tambahkan ke container
            graph_image = Image(texture=texture, allow_stretch=True, keep_ratio=False)
            self.ids.graph_container.add_widget(graph_image)
            plt.close(fig) # Sangat penting untuk menutup figure Matplotlib agar tidak memori leak

class WeatherApp(App):
    """Kelas utama aplikasi Kivy."""
    def build(self):
        self.title = "Aplikasi Prediksi Cuaca Misha"
        return WeatherRoot()

if __name__ == '__main__':
    # Pastikan folder 'model' ada
    if not os.path.exists('model'):
        os.makedirs('model')
    
    # Pastikan folder 'assets/icons' ada
    if not os.path.exists('assets/icon'):
        os.makedirs('assets/icon')
    
    # Jalankan aplikasi Kivy
    WeatherApp().run()