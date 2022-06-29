import math

from kivy.app import App
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.clock import Clock


class HumanEval(App):
    def on_start(self):
        Clock.schedule_interval(self.root.ids.eval_bar.update, 1 / 60)


class EvalBar(Widget):
    current_eval = NumericProperty(0)
    wiggle = NumericProperty(0)
    wiggle_height = dp(5)
    color = Color(rgb=(1, 1, 1))
    rect = Rectangle
    elapsed_time = 0

    def update(self, dt):
        self.wiggle = self.wiggle_height * math.sin(self.elapsed_time)
        self.elapsed_time += 2 * dt

    # def draw_bar(self, eval_out_of_100):
    #     half_height = self.height / 2
    #     eval_as_decimal = eval_out_of_100 / 100
    #     target_height = half_height + (half_height * eval_as_decimal)
    #     with self.canvas.before:
    #         Color(self.color)
    #         self.rect = Rectangle(pos=self.pos, size=(self.width, target_height))

    def set_eval(self, new_eval_out_of_100):
        self.current_eval = new_eval_out_of_100


class EvalButtonGrid(GridLayout):
    player_color = StringProperty()
    button_bindings = {Button: (str, int)}
    evaluations = []
    direction = 1
    eval_bar = ObjectProperty(EvalBar)

    def set_player_color(self, color_name):
        if color_name != "White":
            self.direction = -1
        self.evaluations = [(f"{color_name} is absolutely crushing", 98), (f"{color_name} is winning", 80),
                            (f"{color_name} is much better", 60), (f"{color_name} is slightly better", 40),
                            (f"{color_name} is pulling", 20), (f"{color_name} is okay", 10)]
        for evaluation in self.evaluations:
            btn = Button(text=evaluation[0])
            self.button_bindings[btn] = evaluation
            btn.bind(on_release=self.set_evaluation)
            self.add_widget(btn)

        return color_name

    def set_evaluation(self, btn):
        new_eval_out_of_100 = self.button_bindings[btn][1]
        if self.player_color == "Black":
            new_eval_out_of_100 *= -1
        self.eval_bar.set_eval(new_eval_out_of_100)


HumanEval().run()
