'''
    Stepper Motor interfacing with Raspberry Pi
    http:///www.electronicwings.com
'''
import RPi.GPIO as GPIO
import time
import sys

# assign GPIO pins for motor
motor_channel = 29, 31, 33, 35
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# for defining more than 1 GPIO channel as input/output use
GPIO.setup(motor_channel, GPIO.OUT)


def step_forward(delay: float):
    GPIO.output(motor_channel, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
    time.sleep(delay)
    GPIO.output(motor_channel, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
    time.sleep(delay)
    GPIO.output(motor_channel, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
    time.sleep(delay)
    GPIO.output(motor_channel, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
    time.sleep(delay)


def step_backward(delay: float):
    GPIO.output(motor_channel, (GPIO.HIGH, GPIO.LOW, GPIO.LOW, GPIO.HIGH))
    time.sleep(delay)
    GPIO.output(motor_channel, (GPIO.LOW, GPIO.LOW, GPIO.HIGH, GPIO.HIGH))
    time.sleep(delay)
    GPIO.output(motor_channel, (GPIO.LOW, GPIO.HIGH, GPIO.HIGH, GPIO.LOW))
    time.sleep(delay)
    GPIO.output(motor_channel, (GPIO.HIGH, GPIO.HIGH, GPIO.LOW, GPIO.LOW))
    time.sleep(delay)


def move_distance(speed: float, distance_deg: float):
    assert -500. <= speed <= 500.

    if speed != 0.:
        p = abs(1. / speed)
        ratio = 360. / 512.
        distance_abs = abs(distance_deg)

        total = 0.
        if (0. < speed) == (0. < distance_deg):
            while total < distance_abs:
                step_forward(p)
                total += ratio
        else:
            while total < distance_abs:
                step_backward(p)
                total += ratio


if __name__ == "__main__":
    while True:
        selected_speed = float(input("speed [-500, 500]: "))
        selected_distance = float(input("distance [0, 360]: "))
        move_distance(selected_speed, selected_distance)
