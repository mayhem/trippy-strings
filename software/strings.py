#!/usr/bin/env python3

from math import sin
from time import sleep, time
from threading import Thread
import pigpio
from encoder import decoder
from simple_pid import PID

HALL_1_0 = 17
HALL_1_1 = 27
HALL_2_0 = 24
HALL_2_1 = 25
MOTOR_1 = 12
MOTOR_2 = 13

WINDOW_SIZE = 5
SAMPLE_TIME = .075
SET_POINT_ADJUST_INCREMENT = 25

ts = None
def callback_0(way):
    ts.callback_0(way)

def callback_1(way):
    ts.callback_1(way)

def pig_callback(GPIO, level, tick):
    ts.pig_callback(GPIO, level, tick)


class TrippyStrings(object):

    def __init__(self):
        self.P = 1.0
        self.I = .1
        self.D = .05
        self.pid = None
        self.speed = 0
        self.set_point = 0

        self.pi = pigpio.pi()  
        self.pi.set_mode(MOTOR_1, pigpio.OUTPUT)
        self.pi.set_mode(MOTOR_2, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(MOTOR_1,800)
        self.pi.set_PWM_frequency(MOTOR_2,800)
        self.pi.set_PWM_range(MOTOR_1, 255)
        self.pi.set_PWM_range(MOTOR_2, 255)
        self.encoder_0 = decoder(self.pi, HALL_1_0, HALL_1_1, callback_0)
        self.encoder_1 = decoder(self.pi, HALL_2_0, HALL_2_1, callback_1)
        self.pos_0 = 0
        self.pos_1 = 0


    def setup(self):
        if not self.pi.connected:
           sys.exit(-1)

    def stop(self):
        self.motor_speed(0, 0)
        self.motor_speed(1, 0)


    def callback_0(self, way):
        self.pos_0 += way


    def callback_1(self, way):
        self.pos_1 += way


    def motor_speed(self, motor, speed):
        if motor != 0 and motor != 1 and (speed < -255 or speed > 255):
            return

        pin = (MOTOR_1, MOTOR_2)[motor]
        print("%d %d" % (pin, speed))
        self.pi.set_PWM_dutycycle(pin, speed) 


    def test(self):

        self.motor_speed(0, 250)
        self.motor_speed(1, 240)
        sleep(5)
        self.motor_speed(0, 0)
        self.motor_speed(1, 0)

    def run(self):

        i = 0
        self.speed = 64

        print("controller ready for action.")
        while True:
            diff = self.pos_1 - self.pos_0
            control = self.pid(self.pos_1 - self.pos_0)
            pwm_diff = min(self.speed * 1.5, control)
            mot_0 = int(self.speed - pwm_diff)
            mot_1 = int(self.speed + pwm_diff)
            self.motor_speed(0, mot_0)
            self.motor_speed(1, mot_1)
#                print("d: %d c: %.2f p: %d 0: %d 1: %d" % (diff, control, pwm_diff, mot_0, mot_1))

            s = sin(time() / 4) * 800
            print(int(s))
            self.pid.setpoint = s

            sleep(SAMPLE_TIME)
            i += 1

        self.motor_speed(0, 0)
        self.motor_speed(1, 0)


def main():
    global ts

    ts = TrippyStrings()
    ts.setup()
    try:
        ts.test()
#        ts.run()
    except KeyboardInterrupt:
        ts.stop()


if __name__ == "__main__":
    main()
