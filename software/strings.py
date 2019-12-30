#!/usr/bin/python3

from time import sleep, time
from threading import Thread
import pigpio
import serial
from encoder import decoder
from simple_pid import PID

BUTTON_0 = 17
BUTTON_1 = 8
HALL_1_0 = 27
HALL_1_1 = 22
HALL_2_0 = 23
HALL_2_1 = 24

DEVICE = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__Arduino_Uno_64932343938351313012-if00"
WINDOW_SIZE = 5
DEBOUNCE_TIME = .01
SAMPLE_TIME = .075

STATE_SETUP = 1
STATE_SETUP_B0 = 2
STATE_SETUP_B1 = 3
STATE_RUNNING = 4
STATE_RUNNING_B0 = 5
STATE_RUNNING_B1 = 6

EVENT_B0_HI= 0
EVENT_B0_LOW = 1
EVENT_B1_HI= 2
EVENT_B1_LOW = 3

transition_table = (
    (STATE_SETUP, EVENT_B0_HI, STATE_SETUP_B0),  
    (STATE_SETUP, EVENT_B1_HI, STATE_SETUP_B1),  

    (STATE_SETUP_B0, EVENT_B1_HI, STATE_RUNNING),
    (STATE_SETUP_B0, EVENT_B0_LOW, STATE_SETUP),
    (STATE_SETUP_B1, EVENT_B0_HI, STATE_RUNNING),
    (STATE_SETUP_B1, EVENT_B1_LOW, STATE_SETUP),

    (STATE_RUNNING, EVENT_B0_HI, STATE_RUNNING_B0),  
    (STATE_RUNNING, EVENT_B1_HI, STATE_RUNNING_B1),  

    (STATE_RUNNING_B0, EVENT_B1_HI, STATE_SETUP),
    (STATE_RUNNING_B0, EVENT_B0_LOW, STATE_RUNNING),
    (STATE_RUNNING_B1, EVENT_B0_HI, STATE_SETUP),
    (STATE_RUNNING_B1, EVENT_B1_LOW, STATE_RUNNING),
)

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

        self.pi = pigpio.pi()  
        self.encoder_0 = decoder(self.pi, HALL_1_0, HALL_1_1, callback_0)
        self.encoder_1 = decoder(self.pi, HALL_2_0, HALL_2_1, callback_1)
        self.button_0_state = False
        self.button_0_change = 0
        self.button_1_state = False
        self.button_1_change = 0
        self.pos_0 = 0
        self.pos_1 = 0
        self.current_state = STATE_SETUP


    def setup(self):
        if not self.pi.connected:
           sys.exit(-1)

        self.pi.callback(BUTTON_0, pigpio.EITHER_EDGE, pig_callback)
        self.pi.callback(BUTTON_1, pigpio.EITHER_EDGE, pig_callback)

        try:
            self.ser = serial.Serial(DEVICE,
                38400,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=.01)
        except serial.serialutil.SerialException as err:
            print("Failed to open serial port %s" % device, str(err))
            sys.exit(-1)

        sleep(1)


    def pig_callback(self, gpio, level, tick):
        if gpio == BUTTON_0 and level:
            self.button_0_change = time()
            self.button_0_state = True

        if gpio == BUTTON_0 and not level:
            self.button_0_change = time()
            self.button_0_state = False

        if gpio == BUTTON_1 and level:
            self.button_1_change = time()
            self.button_1_state = True

        if gpio == BUTTON_1 and not level:
            self.button_1_change = time()
            self.button_1_state = False


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

        # Take into account that one motor is upside down from the other
        if motor == 1:
            speed = -speed

        if self.ser:
            print(motor, speed)
            self.ser.write(bytes("%d%d\r\n" % (motor, speed), encoding="ascii"))
            

    def event_action(self, new_state, event):
        if new_state == STATE_RUNNING:
            self.pos_0 = 0
            self.pos_1 = 0
            self.motor_speed(0, 64)
            self.motor_speed(1, 64)
            self.pid = PID(self.P, self.I, self.D, setpoint=0)
            self.pid.sample_time = SAMPLE_TIME
            self.speed = 64

        elif new_state == STATE_SETUP:
            self.motor_speed(0, 0)
            self.motor_speed(1, 0)
            self.speed = 0
        elif new_state == STATE_SETUP_B0:
            self.motor_speed(0, 64)
        elif new_state == STATE_SETUP_B1:
            self.motor_speed(1, 64)


    def handle_event(self, event):
        for row in transition_table:
            if row[0] == self.current_state and row[1] == event:
                self.event_action(row[2], event)
                self.current_state = row[2]
#        else:
#            print("warning event not in transition table. current_state: %d event: %d" % (self.current_state, event))
                

    def run(self):

        i = 0
        self.speed = 64

        print("controller ready for action.")
        while True:

            if not self.button_0_state and self.button_0_change and (time() - self.button_0_change > DEBOUNCE_TIME):
                self.handle_event(EVENT_B0_HI)
                self.button_0_change = 0
                self.button_0_state = 1

            if not self.button_1_state and self.button_1_change and (time() - self.button_1_change > DEBOUNCE_TIME):
                self.handle_event(EVENT_B1_HI)
                self.button_1_change = 0
                self.button_1_state = 1

            if self.button_0_state and self.button_0_change and (time() - self.button_0_change > DEBOUNCE_TIME):
                self.handle_event(EVENT_B0_LOW)
                self.button_0_change = 0
                self.button_0_state = 0

            if self.button_1_state and self.button_1_change and (time() - self.button_1_change > DEBOUNCE_TIME):
                self.handle_event(EVENT_B1_LOW)
                self.button_1_change = 0
                self.button_1_state = 0

            if self.pid:
                diff = self.pos_1 - self.pos_0
                control = self.pid(self.pos_1 - self.pos_0)
                pwm_diff = min(self.speed * 1.5, control)
                mot_0 = int(self.speed - pwm_diff)
                mot_1 = int(self.speed + pwm_diff)
                self.motor_speed(0, mot_0)
                self.motor_speed(1, mot_1)
#                print("d: %d c: %.2f p: %d 0: %d 1: %d" % (diff, control, pwm_diff, mot_0, mot_1))

            sleep(SAMPLE_TIME)
            i += 1

        self.motor_speed(0, 0)
        self.motor_speed(1, 0)


def main():
    global ts

    ts = TrippyStrings()
    ts.setup()
    try:
        ts.run()
    except KeyboardInterrupt:
        ts.stop()


if __name__ == "__main__":
    main()
