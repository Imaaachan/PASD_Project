import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import random
import joblib
import pandas as pd
import numpy as np

# ================== MODEL LOADING ==================
models = {
    "cuaca": "model/model_cuaca.pkl",
    "kelembaban": "model/model_kelembaban.pkl",
    "suhu": "model/model_suhu.pkl",
    "tekanan": "model/model_tekanan.pkl"
}

loaded_models = {}
for model_name, model_path in models.items():
    try:
        with open(model_path, 'rb') as file:
            loaded_model = joblib.load(file)
            loaded_models[model_name] = loaded_model
        print(f"Model '{model_name}' berhasil dimuat.")
    except Exception as e:
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

# ================== ANTARMUKA KIVY ==================
class CuacaApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.input = TextInput(hint_text='Masukkan nama kota', multiline=False, size_hint=(1, 0.1))
        self.add_widget(self.input)

        self.button = Button(text='Cek Cuaca', size_hint=(1, 0.1))
        self.button.bind(on_press=self.tampilkan_data)
        self.add_widget(self.button)

        self.hasil = Label(text='', markup=True, size_hint=(1, 0.8))
        self.add_widget(self.hasil)

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

        # Tampilkan prediksi hari ini:
        hasil = f"[b]Prediksi Hari Ini di {kota.title()}[/b]\n"
        hasil += (
            f"Hari ini\n"
            f"Suhu: {suhu_pred:.1f}°C\n"
            f"Kelembapan: {kelembaban_pred:.0f}%\n"
            f"Tekanan: {tekanan_pred:.1f} hPa\n"
            f"{'Hujan' if hujan_pred else 'Tidak Hujan'}\n\n"
        )

        # Tampilkan dummy prediksi 5 hari ke depan:
        hasil += f"[b]Prediksi Cuaca 5 Hari Selanjutnya di {kota.title()}[/b]\n\n"
        for i in range(5):
            hasil += (
                f"Hari ke-{i+1}, "
                f"Suhu: {prediksi['temperature'][i]}°C, "
                f"Kelembapan: {prediksi['humidity'][i]}%, "
                f"Tekanan: {prediksi['pressure'][i]} hPa, "
                f"{'Hujan' if prediksi['rain'][i] else 'Tidak Hujan'}\n"

                # f"Hari ke-{i+1}: {prediksi['temperature'][i]}°C, {prediksi['humidity'][i]}%, "
                # f"{prediksi['pressure'][i]} hPa, {'Hujan' if prediksi['rain'][i] else 'Tidak Hujan'}\n"
            )

        self.hasil.text = hasil

# ================== APLIKASI ==================
class CuacaAppApp(App):
    def build(self):
        return CuacaApp()

if __name__ == '__main__':
    CuacaAppApp().run()

# def generate_prediction_data(location_name, model):
#     try:
#         feature_names = list(model.feature_names_in_)
#         input_df = pd.DataFrame([np.zeros(len(feature_names))], columns=feature_names)

#         location_col = f"Location_{location_name.capitalize()}"
#         if location_col in feature_names:
#             input_df.at[0, location_col] = 1.0
#         else:
#             raise ValueError(f"Lokasi '{location_col}' tidak ditemukan dalam fitur model.")

#         pred = model.predict(input_df)

#         if hasattr(pred, '__len__') and len(pred) >= 5:
#             return list(pred[:5])
#         else:
#             return [float(pred[0])] * 5
#     except Exception as e:
#         print(f"[WARNING!] Gagal prediksi lokasi '{location_name}': {e}")
#         return None

# def generate_prediction_data(location_name, model):
#     try:
#         n_features = len(model.feature_names_in_)
#         input_array = np.zeros((1, n_features))
#         feature_names = model.feature_names_in_

#         # One-hot encode lokasi
#         location_col = f"Location_{location_name.capitalize()}"
#         if location_col in feature_names:
#             loc_index = list(feature_names).index(location_col)
#             input_array[0, loc_index] = 1.0
#         else:
#             raise ValueError(f"Lokasi '{location_col}' tidak ditemukan dalam fitur model.")

#         pred = model.predict(input_array)

#         if hasattr(pred, '__len__') and len(pred) >= 7:
#             return list(pred[:7])
#         else:
#             return [float(pred[0])] * 7
#     except Exception as e:
#         print(f"[WARNING] Gagal prediksi lokasi '{location_name}': {e}")
#         return None

    # def tampilkan_data(self, instance):
    #     kota = self.input.text.strip()
    #     if not kota:
    #         self.hasil.text = "Masukkan nama kota terlebih dahulu."
    #         return

    #     try:
    #         suhu = generate_prediction_data(kota, loaded_models.get("suhu")) or generate_dummy_weather()["temperature"]
    #         kelembaban = generate_prediction_data(kota, loaded_models.get("kelembaban")) or generate_dummy_weather()["humidity"]
    #         tekanan = generate_prediction_data(kota, loaded_models.get("tekanan")) or generate_dummy_weather()["pressure"]
    #         hujan = generate_prediction_data(kota, loaded_models.get("cuaca")) or generate_dummy_weather()["rain"]

    #         teks = f"[b]Prediksi Cuaca 5 Hari di {kota.title()}[/b]\n\n"
    #         for i in range(5):
    #             teks += f"Hari ke-{i+1}: {suhu[i]}°C, {kelembaban[i]}%, {tekanan[i]} hPa, {'Hujan' if hujan[i] else 'Tidak Hujan'}\n"

    #         self.hasil.text = teks
    #     except Exception as e:
    #         self.hasil.text = f"Terjadi error: {str(e)}"