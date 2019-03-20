import enum
import random
import time
from collections import deque
from typing import Dict, Optional, Type
from PIL import Image, ImageDraw

import RPi.GPIO


class Display:
    _display = Adafruit_SSD1306.SSD1306_128_64(rst=24)
    _display.begin()
    _display.clear()
    _display.display()

    width = _display.width
    height = _display.height
    _image = Image.new("1", (width, height))

    draw = ImageDraw.Draw(_image)


class Pin(enum.Enum):
    # BOARD layout!
    up = 11
    down = 15
    left = 13
    right = 16

    center = 7

    five = 29
    six = 31


class Menu:
    _identity = -1

    def __init__(self, sub_menus: Optional[Dict[Pin, "Menu"]] = None):
        Menu._identity += 1
        self._identity = Menu._identity

        if sub_menus is None:
            self.sub_menus = dict()
        else:
            self.sub_menus = sub_menus

    def __hash__(self) -> int:
        return self._identity

    def draw(self):
        raise NotImplementedError()

    def send_input(self, pin_input: Pin):
        raise NotImplementedError()


class AdaFruitMenu:
    def __init__(self, main_menu: Menu, pins: Type[Pin]):
        self._pins = pins
        self._back_pin = self._pins.six

        self._last_menu = deque(maxlen=1000)
        self._current_menu = main_menu

        RPi.GPIO.setmode(RPi.GPIO.BOARD)
        for _each_pin in self._pins:
            RPi.GPIO.setup(_each_pin, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

    def button_released(self) -> Optional[Pin]:
        for _each_pin in self._pins:
            if RPi.GPIO.input(_each_pin):
                return _each_pin

        return None

    def loop(self):
        while True:
            pin_input = self.button_released()
            if pin_input is not None:
                if pin_input == self._back_pin:
                    if 0 < len(self._last_menu):
                        self._current_menu = self._last_menu.pop()

                else:
                    self._current_menu.send_input(pin_input)

                    new_menu = self._current_menu.sub_menus.get(pin_input)
                    if new_menu is not None:
                        self._last_menu.append(self._current_menu)
                        self._current_menu = new_menu

                    time.sleep(.01)

            self._current_menu.draw()


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self._text = "<empty>"

    def draw(self):
        Display.draw.text(64, 32, self._text)

    def send_input(self, pin_input: Pin):
        self._text = "{:.04f}".format(random.random())


def main():
    main_menu = MainMenu()
    ada_menu = AdaFruitMenu(main_menu, Pin)
    ada_menu.loop()
