#!/usr/bin/env python3

from math import sin
from time import sleep, time
import sys
import pigpio
import serial

DEVICE = "/dev/ttyAMA0"

def send(ser, cmd):
    ser.write(bytes(cmd + "\n", "utf-8"))


try:
    ser = serial.Serial(DEVICE,
        38400,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=.01)
except serial.serialutil.SerialException as err:
    print("Failed to open serial port %s" % DEVICE, str(err))
    sys.exit(-1)

print("waking up")
sleep(1)

send(ser, "EM,3,3")
send(ser, "SM,1000,0,0")
send(ser, "SM,1000,5000,0")
send(ser, "SM,1000,0,5000")
send(ser, "SM,1000,0,0")
