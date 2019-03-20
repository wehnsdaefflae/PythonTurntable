import RPi.GPIO

import enum
import random
import time
from typing import Dict, Optional, Type, Set
from PIL import Image, ImageDraw, ImageFont

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from motor import MotorControl


class Display:
    display = Adafruit_SSD1306.SSD1306_128_64(rst=24)
    display.begin()
    display.clear()
    display.display()

    width = display.width
    height = display.height
    image = Image.new("1", (width, height))

    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()


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
        Display.display.clear()
        Display.draw.rectangle((0, 0, Display.width, Display.height), outline=0, fill=0)

        self._draw()

        Display.display.image(Display.image)
        Display.display.display()

    def send_input(self, pin_input: Set[Pin]):
        raise NotImplementedError()


class AdaFruitMenu:
    def __init__(self, main_menu: Menu, pins: Type[Pin]):
        self._pins = pins
        self._back_pin = self._pins.six

        self._current_menu = main_menu
        self._pressed = set()

        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(tuple(_each_pin.value for _each_pin in self._pins), RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

    def _update_input_state(self):
        for _each_pin in self._pins:
            if RPi.GPIO.input(_each_pin.value):
                self._pressed.discard(_each_pin)
            else:
                self._pressed.add(_each_pin)

    def loop(self):
        while True:
            self._update_input_state()

            self._current_menu.send_input(self._pressed)
            self._current_menu.draw()

            time.sleep(.01)


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self._no_photos = 36

    def _draw(self):
        Display.draw.text((10, 30), "{:03d}".format(self._no_photos), font=Display.font, fill=255)

        Display.draw.text((40, 20), "+5", font=Display.font, fill=155)
        Display.draw.text((40, 40), "-5", font=Display.font, fill=155)
        Display.draw.text((30, 30), "-1", font=Display.font, fill=155)
        Display.draw.text((50, 30), "+1", font=Display.font, fill=155)

        Display.draw.text((80, 20), "confirm", font=Display.font, fill=155)
        Display.draw.text((70, 40), "reset", font=Display.font, fill=155)

    def send_input(self, pin_input: Set[Pin]):
        if Pin.up in pin_input:
            self._no_photos = min(self._no_photos + 5, 359)

        elif Pin.down in pin_input:
            self._no_photos = max(self._no_photos - 5, 0)

        elif Pin.left in pin_input:
            self._no_photos = max(self._no_photos - 1, 0)

        elif Pin.right in pin_input:
            self._no_photos = min(self._no_photos + 1, 359)

        elif Pin.five in pin_input:
            self._no_photos = 36

        elif Pin.six in pin_input:
            print("starting {:0d} photos".format(self._no_photos))
            MotorControl.start_recording(self._no_photos)


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
