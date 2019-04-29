
# ==============================================================
# This file is exclusively used to simulate the PWM object from
# the RPi.GPIO module, so the program can be run on a
# non-raspberry-pi device.
# ==============================================================

class PWM:
    def __init__(self):
        pass

    def start(self, val):
        return

    def ChangeDutyCycle(self, val):
        return