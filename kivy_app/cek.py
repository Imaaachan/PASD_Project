from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.clock import Clock

class GraphWidget(Widget):
    points = ListProperty([])
    min_val = NumericProperty(0)
    max_val = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_graph, size=self.update_graph, points=self.update_graph)
        Clock.schedule_once(self.update_graph)

    def update_graph(self, *args):
        self.canvas.clear()
        if not self.points:
            return

        with self.canvas:
            Color(0.6, 0.2, 0.8, 1) # Ungu

            x_scale = self.width / (len(self.points) - 1) if len(self.points) > 1 else self.width
            y_range = self.max_val - self.min_val if (self.max_val - self.min_val) > 0 else 1
            y_scale = self.height / y_range

            canvas_points = []
            for i, val in enumerate(self.points):
                x = self.x + i * x_scale
                y = self.y + (val - self.min_val) * y_scale
                canvas_points.extend([x, y])

            Line(points=canvas_points, width=2)
            pass

class CekAppUI(FloatLayout): # Nama kelas UI utama
    current_city = StringProperty("Sydney")
    current_temp = NumericProperty(20)
    current_condition = StringProperty("Mostly Clear")

    daily_forecast_data = ListProperty([
        {"day": "MON", "temp": 19, "prob": 30, "icon": "cloudy.png"},
        {"day": "TUE", "temp": 20, "prob": 0, "icon": "sunny.png"},
        {"day": "WED", "temp": 19, "prob": 0, "icon": "cloudy.png"},
        {"day": "THUR", "temp": 18, "prob": 0, "icon": "rainy.png"},
        {"day": "FRI", "temp": 18, "prob": 0, "icon": "sunny.png"},
    ])

    graph_temps = ListProperty([19, 20, 19, 18, 18])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(graph_temps=self.update_graph_widget_data)
        Clock.schedule_once(self.update_graph_widget_data)

    def update_graph_widget_data(self, *args):
        if self.ids.weather_graph:
            self.ids.weather_graph.points = self.graph_temps
            self.ids.weather_graph.min_val = min(self.graph_temps) - 2
            self.ids.weather_graph.max_val = max(self.graph_temps) + 2


class CekApp(App): 
    def build(self):
        return CekAppUI() # Return instance dari CekAppUI

if __name__ == '__main__':
    CekApp().run() # Jalankan CekApp