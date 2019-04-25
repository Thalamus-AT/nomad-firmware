import random

import PWM_Sim

BCM = 0
OUT = 1
IN = 2
PUD_UP = 3

TRIG = None
ping_time = 0


def setwarnings(bool):
    return


def setmode(mode):
    return


def setup(pin, mode, pull_up_down=None):
    return


def output(pin, val):
    return


def input(pin):
    return int(random.random() + 0.1)


def PWM(pin, val):
    return PWM_Sim.PWM()


def cleanup():
    return
