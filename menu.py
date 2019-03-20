import RPi.GPIO

import enum
import random
import time
from collections import deque
from typing import Dict, Optional, Type, Set
from PIL import Image, ImageDraw  # , ImageFont

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306


class Display:
    display = Adafruit_SSD1306.SSD1306_128_64(rst=24)
    display.begin()
    display.clear()
    display.display()

    width = display.width
    height = display.height
    _image = Image.new("1", (width, height))

    draw = ImageDraw.Draw(_image)


class Pin(enum.Enum):
    # BCM layout!
    up = 17
    down = 22
    left = 27
    right = 23

    center = 4

    five = 5
    six = 6


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

    def _draw(self):
        raise NotImplementedError()

    def draw(self):
        self._draw()
        Display.display.display()

    def send_input(self, pin_input: Set[Pin]):
        raise NotImplementedError()


class AdaFruitMenu:
    def __init__(self, main_menu: Menu, pins: Type[Pin]):
        self._pins = pins
        self._back_pin = self._pins.six

        self._current_menu = main_menu

        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(tuple(_each_pin.value for _each_pin in self._pins), RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

    def buttons_pressed(self) -> Set[Pin]:
        pressed = set()
        for _each_pin in self._pins:
            value = RPi.GPIO.input(_each_pin.value)
            if not value:
                pressed.add(_each_pin)

        return pressed

    def loop(self):
        while True:
            pressed = self.buttons_pressed()

            self._current_menu.send_input(pressed)
            self._current_menu.draw()

            time.sleep(.1)


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self._text = "<empty>"

    def _draw(self):
        Display.draw.text((0, 0), self._text)

    def send_input(self, pin_input: Set[Pin]):
        if 0 < len(pin_input):
            self._text = "{:.04f}".format(random.random())


def main():
    RPi.GPIO.cleanup()
    Display.display.clear()

    main_menu = MainMenu()
    ada_menu = AdaFruitMenu(main_menu, Pin)

    try:
        ada_menu.loop()

    except KeyboardInterrupt as e:
        Display.display.clear()
        RPi.GPIO.cleanup()
        raise e


if __name__ == "__main__":
    main()
