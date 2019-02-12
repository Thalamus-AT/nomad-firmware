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

LED_PINS = [12, 13, 16]
leds = [None, None, None]


def setup():
    global leds

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for i in range(len(LED_PINS)):
        GPIO.setup(LED_PINS[i], GPIO.OUT)

    time.sleep(3)

    for i in range(len(LED_PINS)):
        leds[i] = GPIO.PWM(LED_PINS[i], 50)
        leds[i].start(100)


def set_pad_intensity(pad, intensity):
    global leds

    intensities[pad] = int(intensity)

    if leds[pad] is not None:
        leds[pad].ChangeDutyCycle(int(intensities[pad]))


def set_all_intensities(values):
    for i in range(len(leds)):
        val = max(min(values[i], 100), 0)
        set_pad_intensity(i, val)


def get_pad_intensity(pad):
    return intensities[pad]


def close():
    GPIO.cleanup()
