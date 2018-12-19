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


def move_acc(distance_deg: float):
    acc_dist = 10
    if distance_deg < 2. * acc_dist:
        move_distance(20., distance_deg)
    else:
        for _i in range(acc_dist):
            move_distance(8. * _i + 20., 1.)
        move_distance(100., distance_deg - 2. * acc_dist)
        for _i in range(acc_dist):
            move_distance(-8. * _i + 100., 1.)


def trigger_shot():
    print("shot!")


def start_recording(no_photos: int):
    segment = 360. / no_photos
    for _i in range(no_photos):
        trigger_shot()
        print("{:d}/{:d}".format(_i + 1, no_photos))
        move_acc(segment)
        if _i < no_photos - 1:
            time.sleep(1.)


def test_distance_movement():
    while True:
        selected_speed = float(input("speed [-500, 500]: "))
        selected_distance = float(input("distance [0, 360]: "))
        move_distance(selected_speed, selected_distance)


def test_full_circle():
    while True:
        selected_no_photos = int(input("number of photos: "))
        start_recording(selected_no_photos)


if __name__ == "__main__":
    test_full_circle()