
from typing import Callable

import time

import RPi.GPIO


class MotorControl:
    # assign GPIO pins for motor
    motor_channel = 16, 20, 21, 19
    RPi.GPIO.setwarnings(False)
    RPi.GPIO.setmode(RPi.GPIO.BCM)

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
    def move_distance(distance_deg: float, speed_fun: Callable[[float, float], float] = lambda _d, _t: 100.):
        ratio = 360. / 512.
        distance_abs = abs(distance_deg)

        current_total = 0.
        if 0. < distance_deg:
            while current_total < distance_abs:
                current_speed = speed_fun(current_total, distance_abs)
                # print("{:06.2f}° -> {:06.2f}".format(current_total, current_speed))
                MotorControl.step_forward(current_speed)
                current_total += ratio
        else:
            while current_total < distance_abs:
                current_speed = speed_fun(current_total, distance_abs)
                # print("{:06.2f}° -> {:06.2f}".format(current_total, current_speed))
                MotorControl.step_backward(current_speed)
                current_total += ratio

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

    @staticmethod
    def start_recording(no_photos: int):
        if no_photos < 1:
            return

        if no_photos >= 360:
            print("please select a number below 360")

        segment = 360. / no_photos
        for _i in range(no_photos):
            MotorControl.trigger_shot()
            print("{:d}/{:d}".format(_i + 1, no_photos))
            MotorControl.move_distance(segment, speed_fun=MotorControl.speed_function)
            if _i < no_photos - 1:
                time.sleep(1.)
        print("done!")

    @staticmethod
    def test_distance_movement():
        while True:
            selected_speed = float(input("speed [-500, 500]: "))
            selected_distance = float(input("distance [0, 360]: "))
            MotorControl.move_distance(selected_distance, speed_fun=lambda _d, _t: selected_speed)

    @staticmethod
    def test_full_circle():
        while True:
            selected_no_photos = int(input("number of photos: "))
            MotorControl.start_recording(selected_no_photos)


if __name__ == "__main__":
    MotorControl.test_full_circle()
