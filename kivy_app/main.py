from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock

# Kelas layar loading/splash
class SplashScreen(Screen):
    def on_enter(self):
        # switch ke homescreen setelah 3 detik
        Clock.schedule_once(self.switch_to_home, 2)

    def switch_to_home(self, dt):
        self.manager.current = 'home'

#home screen
class HomeScreen(Screen):
    def show_weather(self):
        city = self.ids.city_input.text
        self.ids.weather_label.text = f"Menampilkan data cuaca untuk {city} (dummy)"

    def predict_weather(self):
        self.ids.prediction_label.text = "Prediksi suhu besok: 30°C"

# App utama
class WeatherApp(App):
    def build(self):
        return Builder.load_file("weather.kv")

if __name__ == '__main__':
    WeatherApp().run()
