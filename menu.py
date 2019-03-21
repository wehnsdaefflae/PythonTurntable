import RPi.GPIO

import enum
import time
from typing import Dict, Optional, Type, Set, Callable
from PIL import Image, ImageDraw, ImageFont

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

RPi.GPIO.setmode(RPi.GPIO.BCM)


class Pin(enum.Enum):
    # BCM layout!
    up = 17
    down = 22
    left = 27
    right = 23

    center = 4

    five = 5
    six = 6


class ControlState:
    RPi.GPIO.setup(tuple(_each_pin.value for _each_pin in Pin), RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

    _pressed = set()

    @staticmethod
    def get_inputs() -> Set[Pin]:
        for _each_pin in Pin:
            state = RPi.GPIO.input(_each_pin.value)
            print("{:s}: {:s}".format(_each_pin.name, str(state)))
            if state:
                ControlState._pressed.discard(_each_pin)
            else:
                ControlState._pressed.add(_each_pin)

        return ControlState._pressed


class MotorControl:
    # assign GPIO pins for motor
    motor_channel = 16, 20, 21, 19
    RPi.GPIO.setwarnings(False)

    # for defining more than 1 GPIO channel as input/output use
    RPi.GPIO.setup(motor_channel, RPi.GPIO.OUT)

    @staticmethod
    def step_forward(speed: float):
        assert 0. < speed
        delay = 1. / speed

        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.HIGH, RPi.GPIO.LOW, RPi.GPIO.LOW, RPi.GPIO.HIGH))
        time.sleep(delay)
        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.HIGH, RPi.GPIO.HIGH, RPi.GPIO.LOW, RPi.GPIO.LOW))
        time.sleep(delay)
        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.LOW, RPi.GPIO.HIGH, RPi.GPIO.HIGH, RPi.GPIO.LOW))
        time.sleep(delay)
        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.LOW, RPi.GPIO.LOW, RPi.GPIO.HIGH, RPi.GPIO.HIGH))
        time.sleep(delay)

    @staticmethod
    def step_backward(speed: float):
        assert 0. < speed
        delay = 1. / speed

        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.HIGH, RPi.GPIO.LOW, RPi.GPIO.LOW, RPi.GPIO.HIGH))
        time.sleep(delay)
        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.LOW, RPi.GPIO.LOW, RPi.GPIO.HIGH, RPi.GPIO.HIGH))
        time.sleep(delay)
        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.LOW, RPi.GPIO.HIGH, RPi.GPIO.HIGH, RPi.GPIO.LOW))
        time.sleep(delay)
        RPi.GPIO.output(MotorControl.motor_channel, (RPi.GPIO.HIGH, RPi.GPIO.HIGH, RPi.GPIO.LOW, RPi.GPIO.LOW))
        time.sleep(delay)

    @staticmethod
    def trigger_shot():
        print("shot!")

    @staticmethod
    def speed_function(current_degree: float, total_degree: float) -> float:
        max_speed = 100.
        min_speed = 20.
        change_distance = 10.

        if total_degree < 2. * change_distance:
            return min_speed

        if current_degree < change_distance:
            return (max_speed - min_speed) / change_distance * current_degree + min_speed

        until_slowdown = total_degree - change_distance
        if current_degree >= until_slowdown:
            return (min_speed - max_speed) / change_distance * (current_degree - until_slowdown) + max_speed

        return max_speed


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

    def check_input(self):
        raise NotImplementedError()


class AdaFruitMenu:
    def __init__(self, main_menu: Menu):
        self._current_menu = main_menu

    def loop(self):
        while True:
            self._current_menu.draw()

            time.sleep(.01)


class MainMenu(Menu):
    def __init__(self):
        super().__init__()
        self._no_photos = 36
        self._progress = -1.

    def _draw(self):
        if self._progress < 0.:
            Display.draw.text((5, 30), "{:03d}".format(self._no_photos), font=Display.font, fill=255)

            Display.draw.text((40, 20), "+5", font=Display.font, fill=155)
            Display.draw.text((40, 40), "-5", font=Display.font, fill=155)
            Display.draw.text((30, 30), "-1", font=Display.font, fill=155)
            Display.draw.text((50, 30), "+1", font=Display.font, fill=155)

            Display.draw.text((80, 20), "confirm", font=Display.font, fill=155)
            Display.draw.text((80, 40), "reset", font=Display.font, fill=155)

        else:
            Display.draw.text((20, 5), "finished {:03d}/{:03d}".format(round(self._no_photos * self._progress / 360.), self._no_photos), font=Display.font, fill=255)
            Display.draw.arc((15, 20, Display.display.width - 5, Display.display.height - 10), 0., self._progress, fill=255, width=1)
            Display.draw.text((5, 30), "abort", font=Display.font, fill=255)

    def _move_distance(self, distance_deg: float, speed_fun: Callable[[float, float], float] = lambda _d, _t: 100.) -> float:
        ratio = 360. / 512.
        distance_abs = abs(distance_deg)

        current_total = 0.
        if 0. < distance_deg:
            while current_total < distance_abs:
                current_speed = speed_fun(current_total, distance_abs)
                MotorControl.step_forward(current_speed)
                current_total += ratio

                control_state = ControlState.get_inputs()
                if Pin.center in control_state:
                    return -1.

        else:
            while current_total < distance_abs:
                current_speed = speed_fun(current_total, distance_abs)
                MotorControl.step_backward(current_speed)
                current_total += ratio

                control_state = ControlState.get_inputs()
                if Pin.center in control_state:
                    return -1.

        return current_total

    def _start_recording(self, no_photos: int):
        if no_photos < 1:
            return

        if no_photos >= 360:
            print("please select a number below 360")

        self._progress = 0.
        segment = 360. / no_photos
        for _i in range(no_photos):
            self.draw()

            MotorControl.trigger_shot()
            print("{:d}/{:d}".format(_i + 1, no_photos))

            distance = self._move_distance(segment, speed_fun=MotorControl.speed_function)
            if distance < 0.:
                print("cancelled!")
                break

            self._progress += segment

            if _i < no_photos - 1:
                time.sleep(1.)

        self._progress = -1.
        print("done!")

    def check_input(self):
        pin_input = ControlState.get_inputs()

        if self._progress < .0:
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
                self._start_recording(self._no_photos)


def main():
    Display.display.clear()

    main_menu = MainMenu()
    ada_menu = AdaFruitMenu(main_menu)

    try:
        ada_menu.loop()

    except KeyboardInterrupt as e:
        Display.display.clear()
        raise e


if __name__ == "__main__":
    try:
        main()

    finally:
        RPi.GPIO.cleanup()
