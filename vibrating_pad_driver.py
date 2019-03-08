import array
import os
import time

# Check the system we are running on, if it is 64 bit we can presume it isn't the Pi
if os.uname()[4] == 'x86_64':
    import GPIO_Sim as GPIO
else:
    import RPi.GPIO as GPIO

intensities = array.array('I', [0, 0, 0])
running = True

ENABLE_PINS = [4, 4, 4]
CLOCKWISE_PIN = [10, 11, 9]
pads = [None] * len(ENABLE_PINS)

STARTUP_FADEIN_SPEED = 6
STARTUP_FADEOUT_SPEED = 8
LOW_BATTERY_PULSES = 2
FAULTY_BIG_PULSES = 3


def setup():
    global pads

    for i in range(len(ENABLE_PINS)):
        GPIO.setup(ENABLE_PINS[i], GPIO.OUT)
        GPIO.setup(CLOCKWISE_PIN[i], GPIO.OUT)

        GPIO.output(ENABLE_PINS[i], True)

        pads[i] = GPIO.PWM(CLOCKWISE_PIN[i], 50)
        pads[i].start(100)


def set_pad_intensity(pad, intensity):
    global pads

    intensities[pad] = int(intensity)

    if pads[pad] is not None:
        pads[pad].ChangeDutyCycle(int(intensities[pad]))


def set_all_intensities(values):
    for i in range(len(pads)):
        val = max(min(values[i], 100), 0)
        set_pad_intensity(i, val)
    return


def get_pad_intensity(pad):
    return intensities[pad]


def close():
    for i in range(len(ENABLE_PINS)):
        GPIO.output(ENABLE_PINS[i], False)
        GPIO.output(CLOCKWISE_PIN[i], False)

    GPIO.cleanup()


def startup_sequence():
    # part = 0
    #
    # i = 0
    # while part == 0:
    #     if i >= 100:
    #         i = 100
    #         part = 1
    #     else:
    #         set_all_intensities([i, i, i])
    #         i = i + STARTUP_FADE_SPEED
    #     time.sleep(0.1)
    #
    # while part == 1:
    #     if i <= 0:
    #         i = 0
    #         part = 2
    #     else:
    #         set_pad_intensity(0, i)
    #         set_pad_intensity(1, i)
    #         set_pad_intensity(2, i)
    #         i = i - 8
    #     time.sleep(0.1)

    i = 0
    while i <= 100:
        set_all_intensities([i, i, i])
        i += STARTUP_FADEIN_SPEED
        time.sleep(0.1)

    i = 100
    while i >= 0:
        set_all_intensities([i, i, i])
        i -= STARTUP_FADEOUT_SPEED
        time.sleep(0.1)


def low_battery_sequence():
    set_all_intensities([0, 0, 0])
    time.sleep(0.4)
    for i in range(LOW_BATTERY_PULSES):
        set_all_intensities([100, 100, 100])
        time.sleep(0.2)
        set_all_intensities([0, 0, 0])
        time.sleep(0.2)
    time.sleep(0.2)


def faulty_sensor_sequence(sensor):
    pad = sensor % 3
    top = False
    if sensor < 3:
        top = True

    set_all_intensities([0, 0, 0])
    time.sleep(0.4)
    for i in range(FAULTY_BIG_PULSES):
        set_all_intensities([100, 100, 100])
        time.sleep(0.2)
        set_all_intensities([0, 0, 0])
        time.sleep(0.2)

    for i in range(2):
        set_pad_intensity(pad, 100)
        time.sleep(0.2)
        set_pad_intensity(pad, 0)
        time.sleep(0.2)

    if top:
        set_pad_intensity(pad, 100)
        time.sleep(0.2)
        set_pad_intensity(pad, 0)

    set_all_intensities([0, 0, 0])
    time.sleep(0.4)
