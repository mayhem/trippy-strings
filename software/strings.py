#!/usr/bin/python3

from time import sleep, time
from threading import Thread
import pigpio
from encoder import decoder

BUTTON_0 = 17
BUTTON_1 = 8
HALL_1_0 = 27
HALL_1_1 = 22
HALL_2_0 = 23
HALL_2_1 = 24

WINDOW_SIZE = 5

ts = None
def callback_0(way):
    ts.callback_0(way)

def callback_1(way):
    ts.callback_1(way)


class TrippyStrings(Thread):

    def __init__(self):
        Thread.__init__(self)

        self.pi = pigpio.pi()  
        self.encoder_0 = decoder(self.pi, HALL_1_0, HALL_1_1, callback_0)
        self.encoder_1 = decoder(self.pi, HALL_2_0, HALL_2_1, callback_1)
        self.stop_thread = False
        self.button_0_state = False
        self.button_1_state = False
        self.pos_0 = 0
        self.pos_1 = 0


    def stop(self):
        self.stop_thread = True


    def callback_0(self, way):
        self.pos_0 += way


    def callback_1(self, way):
        self.pos_1 += way


    def run(self):
        while not self.stop_thread:
#            val = GPIO.input(HALL_2_0)
#            if self.hall_2_state != val:
#                self.hall_2_state = val
#                self.motor_1_ticks.insert(0, time())
#
#            val = GPIO.input(HALL_2_1)
#            if self.hall_3_state != val:
#                self.hall_3_state = val
#                self.motor_1_ticks.insert(0, time())
#
            sleep(.001)




def setup():

#    GPIO.setup(BUTTON_0, GPIO.IN)
#    GPIO.setup(BUTTON_1, GPIO.IN)
    pass


def main():
    global ts

    setup()

    ts = TrippyStrings()
    ts.start()

    try:
        while True:
            print("%04d %04d" % (ts.pos_0, ts.pos_1))
            sleep(.1)
    except KeyboardInterrupt:
        ts.stop()
        ts.join()


if __name__ == "__main__":
    main()
