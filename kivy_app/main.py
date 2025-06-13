import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import random
import joblib
import pandas as pd
import numpy as np
import os
import json

# ================== MODEL LOADING ==================
models = {
    "cuaca": "model/model_cuaca.pkl",
    "kelembaban": "model/model_kelembaban.pkl",
    "suhu": "model/model_suhu.pkl",
    "tekanan": "model/model_tekanan.pkl"
}

loaded_models = {}
load_errors = []

for model_name, model_path in models.items():
    try:
        with open(model_path, 'rb') as file:
            loaded_model = joblib.load(file)
            loaded_models[model_name] = loaded_model
        print(f"Model '{model_name}' berhasil dimuat.")
    except Exception as e:
        load_errors.append(model_name)
        print(f"[ERROR] Gagal memuat model {model_name}: {e}")

# ================== FUNGSI FALLBACK (ACAK) ==================
def generate_dummy_weather():
    return {
        "temperature": [round(random.uniform(10.0, 35.0), 1) for _ in range(5)],
        "humidity": [random.randint(30, 100) for _ in range(5)],
        "pressure": [round(random.uniform(1000, 1025), 1) for _ in range(5)],
        "rain": [random.choices([0, 1], weights=[70, 30])[0] for _ in range(5)],
    }

# ================== FUNGSI PREDIKSI ==================
def generate_prediction_data(location_name, model):
    location_feature_name = f"Location_{location_name.title()}"
    feature_names = model.feature_names_in_ if hasattr(model, 'feature_names_in_') else []

    if location_feature_name not in feature_names:
        raise ValueError(f"Lokasi '{location_name}' tidak tersedia. Silakan masukkan nama kota yang valid.")

    data = pd.DataFrame(np.zeros((1, len(feature_names))), columns=feature_names)
    data[location_feature_name] = 1.0
    return data

# ================== LAYAR UTAMA ==================
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.input = TextInput(hint_text='Masukkan nama kota', multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.input)

        self.button = Button(text='Cek Cuaca', size_hint=(1, 0.1))
        self.button.bind(on_press=self.tampilkan_data)
        layout.add_widget(self.button)

        self.hasil = Label(text='', markup=True, size_hint=(1, 0.7))
        layout.add_widget(self.hasil)

        self.setting_button = Button(text='Settings', size_hint=(1, 0.1))
        self.setting_button.bind(on_press=self.go_to_settings)
        layout.add_widget(self.setting_button)

        self.add_widget(layout)

    def tampilkan_data(self, instance):
        kota = self.input.text.strip()
        if not kota:
            self.hasil.text = "Masukkan nama kota terlebih dahulu."
            return

        try:
            suhu_pred = loaded_models['suhu'].predict(generate_prediction_data(kota, loaded_models['suhu']))[0]
            kelembaban_pred = loaded_models['kelembaban'].predict(generate_prediction_data(kota, loaded_models['kelembaban']))[0]
            tekanan_pred = loaded_models['tekanan'].predict(generate_prediction_data(kota, loaded_models['tekanan']))[0]
            hujan_pred = loaded_models['cuaca'].predict(generate_prediction_data(kota, loaded_models['cuaca']))[0]
        except ValueError as ve:
            self.hasil.text = f"[b]Error:[/b] {ve}"
            return

        prediksi = generate_dummy_weather()
        app = App.get_running_app()
        suhu = self.convert_temperature(suhu_pred)
        tekanan = self.convert_pressure(tekanan_pred)
        temp_unit = '°F' if app.unit_temperature == 'F' else '°C'
        pressure_unit = 'mmHg' if app.unit_pressure == 'mmHg' else 'hPa'

        hasil = f"[b]Prediksi Hari Ini di {kota.title()}[/b]\n"
        hasil += (
            f"Suhu: {suhu:.1f}{temp_unit}\n"
            f"Kelembapan: {kelembaban_pred:.0f}%\n"
            f"Tekanan: {tekanan:.1f} {pressure_unit}\n"
            f"{'Hujan' if hujan_pred else 'Tidak Hujan'}\n"
        )

        hasil += "\n" + "-"*40 + "\n\n"
        hasil += f"[b]Prediksi Cuaca 5 Hari Selanjutnya[/b]\n\n"

        for i in range(5):
            suhu_hari = self.convert_temperature(prediksi['temperature'][i])
            tekanan_hari = self.convert_pressure(prediksi['pressure'][i])
            hasil += (
                f"Hari ke-{i+1}, "
                f"Suhu: {suhu_hari:.1f}{temp_unit}, "
                f"Kelembapan: {prediksi['humidity'][i]}%, "
                f"Tekanan: {tekanan_hari:.1f} {pressure_unit}, "
                f"{'Hujan' if prediksi['rain'][i] else 'Tidak Hujan'}\n"
            )

        if load_errors:
            hasil += f"\n[i]Catatan: Model yang gagal dimuat: {', '.join(load_errors)}[/i]"

        self.hasil.text = hasil

    def go_to_settings(self, instance):
        self.manager.current = 'settings'

    def convert_temperature(self, temp_c):
        if App.get_running_app().unit_temperature == 'F':
            return (temp_c * 9/5) + 32
        return temp_c

    def convert_pressure(self, pressure_hpa):
        if App.get_running_app().unit_pressure == 'mmHg':
            return pressure_hpa * 0.750062
        return pressure_hpa

# ================== LAYAR PENGATURAN ==================
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.info = Label(text='[b]Pengaturan Konversi[/b]', markup=True, size_hint=(1, 0.2))
        layout.add_widget(self.info)

        self.c_to_f = Button(text='Ubah Suhu ke Fahrenheit / Celsius', size_hint=(1, 0.2))
        self.c_to_f.bind(on_press=self.convert_temp)
        layout.add_widget(self.c_to_f)

        self.hpa_to_mmhg = Button(text='Ubah Tekanan ke mmHg / hPa', size_hint=(1, 0.2))
        self.hpa_to_mmhg.bind(on_press=self.convert_pressure)
        layout.add_widget(self.hpa_to_mmhg)

        self.reset = Button(text='Reset ke Default', size_hint=(1, 0.2))
        self.reset.bind(on_press=self.reset_default)
        layout.add_widget(self.reset)

        self.back = Button(text='Kembali ke Home', size_hint=(1, 0.2))
        self.back.bind(on_press=self.go_back)
        layout.add_widget(self.back)

        self.add_widget(layout)

    def convert_temp(self, instance):
        app = App.get_running_app()
        app.unit_temperature = 'F' if app.unit_temperature == 'C' else 'C'
        self.info.text = f"[b]Suhu sekarang dalam {app.unit_temperature}[/b]"

    def convert_pressure(self, instance):
        app = App.get_running_app()
        app.unit_pressure = 'mmHg' if app.unit_pressure == 'hPa' else 'hPa'
        self.info.text = f"[b]Tekanan sekarang dalam {app.unit_pressure}[/b]"

    def reset_default(self, instance):
        app = App.get_running_app()
        app.unit_temperature = 'C'
        app.unit_pressure = 'hPa'
        self.info.text = "[b]Pengaturan dikembalikan ke default (°C dan hPa).[/b]"

    def go_back(self, instance):
        self.manager.current = 'home'

# ================== APLIKASI UTAMA ==================
class CuacaAppApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.unit_temperature = 'C'
        self.unit_pressure = 'hPa'

    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm

if __name__ == '__main__':
    CuacaAppApp().run()
