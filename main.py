import math
from random import random

from kivy.app import App
from kivy.graphics import Color, Rectangle, Line, Ellipse
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
    target_eval = NumericProperty(0)
    size_property = ObjectProperty()
    wiggle = NumericProperty(0)
    wiggle_height = dp(5)
    color = Color(rgb=(1, 1, 1))
    rect = Rectangle
    elapsed_time = 0
    previous_sin_value = 0
    previous_direction_increasing = False
    list_of_bubbles = []
    bar_size = (0, 0)
    white_eval_label = ObjectProperty(Label)
    black_eval_label = ObjectProperty(Label)
    eval_to_symbol = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(rgb=(1, 1, 1))
            self.rect = Rectangle(pos=self.pos, size=self.calculate_bar_size())

    def calculate_bar_size(self):
        self.bar_size = self.width, (self.height / 2) + (self.height / 2 * self.current_eval) + self.wiggle
        return self.bar_size

    def update_rect(self):
        self.rect.pos = self.pos
        self.rect.size = self.bar_size

    def calculate_wiggle(self, dt):

        current_sin_value = math.sin(self.elapsed_time)
        current_direction_increasing = abs(current_sin_value) > abs(self.previous_sin_value)

        # if self.previous_direction_increasing and not current_direction_increasing:
        #     if current_sin_value > 0 and self.target_eval >0:
        #         for i in range(20):
        #             self.spray_bubbles(dt)
        #     elif current_sin_value < 0 and self.target_eval < 0:
        #         for i in range(20):
        #             self.spray_bubbles(dt)

        self.wiggle = self.wiggle_height * current_sin_value
        self.elapsed_time += 2.5 * dt
        if self.current_eval != self.target_eval:
            self.current_eval += (self.target_eval - self.current_eval) / 10

        self.previous_sin_value = current_sin_value
        self.previous_direction_increasing = current_direction_increasing

    def spray_bubbles(self, dt):

        bubble = Bubble(self.target_eval, self, (self.x + (random() * self.width / 2), self.y + self.bar_size[1]))
        self.add_widget(bubble)
        self.list_of_bubbles.append(bubble)

    def update_eval_labels(self):
        if self.target_eval < 0:
            self.white_eval_label.text = ""
            self.black_eval_label.text = self.eval_to_symbol[self.target_eval]
            return
        if self.target_eval > 0:
            self.black_eval_label.text = ""
            self.white_eval_label.text = self.eval_to_symbol[self.target_eval]
        if self.target_eval == 0:
            self.black_eval_label.text = ""
            self.white_eval_label.text = ""

    def update(self, dt):
        self.calculate_wiggle(dt)
        self.calculate_bar_size()
        self.update_rect()
        self.update_eval_labels()
        # for bubble in self.list_of_bubbles:
        #     bubble.update(dt)

    # def draw_bar(self, eval_out_of_100):
    #     half_height = self.height / 2
    #     eval_as_decimal = eval_out_of_100 / 100
    #     target_height = half_height + (half_height * eval_as_decimal)
    #     with self.canvas.before:
    #         Color(self.color)
    #         self.rect = Rectangle(pos=self.pos, size=(self.width, target_height))

    def set_eval(self, new_eval_out_of_100):
        self.target_eval = new_eval_out_of_100


class Bubble(Widget):
    speed = 2
    direction = 1
    shrink_speed = 20
    eval_bar = EvalBar

    def __init__(self, eval, eval_bar, pos, **kwargs):
        super().__init__(**kwargs)
        self.pos = pos
        self.bind(pos=self.update_ellipse_pos)
        self.eval = eval
        self.eval_bar = eval_bar
        self.shrink_speed += (self.shrink_speed * random())
        self.speed += (self.speed * random())
        self.size = (dp(30), dp(30))
        with self.canvas:
            if eval >= 0:
                Color(rgb=(1, 1, 1))
            else:
                Color(rgb=(0, 0, 0))
                self.direction = -1
            self.ellipse = Ellipse(pos=(self.x, self.y), size=self.size)

    def update(self, dt):

        old_width = self.width
        self.size[0] -= self.shrink_speed * dt
        self.size[1] -= self.shrink_speed * dt
        size_change_offset = old_width - self.width

        self.y += self.speed * self.direction
        self.x += self.speed * dt + size_change_offset

        if self.size[0] <= 0:
            self.eval_bar.list_of_bubbles.remove(self)
            self.eval_bar.remove_widget(self)

    def update_ellipse_pos(self, obj, value):
        self.ellipse.pos = (self.x, self.y)
        self.ellipse.size = self.size


class EvalButtonGrid(GridLayout):
    player_color = StringProperty()
    button_bindings = {Button: (str, float, str)}
    evaluations = [str, float, str]
    direction = 1
    eval_bar = ObjectProperty(EvalBar)

    # noinspection PyStatementEffect
    def set_player_color(self, color_name):
        evaluation_to_words = [str, float, str]
        if color_name == "White":
            self.direction = 1
            evaluation_to_words = [(f"{color_name} is absolutely crushing", .99, "!!"),
                                   (f"{color_name} is winning", .75, "+-"),
                                   (f"{color_name} is much better", .6, "+ \n-"),
                                   (f"{color_name} is slightly better", .4, "+="),
                                   (f"{color_name} is pulling", .25, "+\n="), (f"{color_name} is okay", .1, "=")]
        if color_name == "Black":
            self.direction = -1
            evaluation_to_words = [(f"{color_name} is absolutely crushing", -.99, "-!!"),
                                   (f"{color_name} is winning", -.75, "-+"),
                                   (f"{color_name} is much better", -.6, "- \n+"),
                                   (f"{color_name} is slightly better", -.4, "-="),
                                   (f"{color_name} is pulling", -.25, "-\n="), (f"{color_name} is okay", -.1, "=")]

        self.evaluations = evaluation_to_words
        for evaluation in self.evaluations:
            btn = Button(text=evaluation[0], font_size=dp(20))
            self.button_bindings[btn] = evaluation
            btn.bind(on_release=self.set_evaluation)
            self.add_widget(btn)

            self.eval_bar.eval_to_symbol[evaluation[1]] = evaluation[2]

        return color_name

    def set_evaluation(self, btn):
        new_eval_out_of_100 = self.button_bindings[btn][1]

        self.eval_bar.set_eval(new_eval_out_of_100)


HumanEval().run()
