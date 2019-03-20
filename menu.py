import enum
import random
import time
from collections import deque
from typing import Dict, Optional, Type
from PIL import Image, ImageDraw  # , ImageFont

import Adafruit_SSD1306

import RPi.GPIO


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

        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(tuple(_each_pin.value for _each_pin in self._pins), RPi.GPIO.IN, initial=RPi.GPIO.PUD_UP, pull_up_down=RPi.GPIO.PUD_DOWN)

    def button_pressed(self) -> Optional[Pin]:
        for _each_pin in self._pins:
            value = RPi.GPIO.input(_each_pin.value)
            print("{:s}: {:s}".format(_each_pin.name, str(value)))
            if value:
                return _each_pin

        return None

    def loop(self):
        while True:
            pin_input = self.button_pressed()
            if pin_input is not None:
                print("button {:s} has been pressed".format(pin_input.name))

                if pin_input == self._back_pin:
                    if 0 < len(self._last_menu):
                        self._current_menu = self._last_menu.pop()

                else:
                    self._current_menu.send_input(pin_input)

                    new_menu = self._current_menu.sub_menus.get(pin_input)
                    if new_menu is None:
                        pass
                        # time.sleep(.01)

                    else:
                        self._last_menu.append(self._current_menu)
                        self._current_menu = new_menu

            self._current_menu.draw()
            time.sleep(.1)


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self._text = "<empty>"

    def draw(self):
        Display.draw.text((64, 32), self._text)
        Display.display.display()

    def send_input(self, pin_input: Pin):
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
