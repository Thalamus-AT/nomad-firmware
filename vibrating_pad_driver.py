import array
import os

# Check the system we are running on, if it is 64 bit we can presume it isn't the Pi
if os.uname()[4] == 'x86_64':
    import GPIO_Sim as GPIO
else:
    import RPi.GPIO as GPIO

intensities = array.array('I', [0, 0, 0])
running = True

ENABLE_PINS = []
CLOCKWISE_PIN = []
pads = [None] * len(ENABLE_PINS)


def setup():
    global pads

    for i in range(len(ENABLE_PINS)):
        GPIO.setup(ENABLE_PINS[i], GPIO.OUT)
        GPIO.setup(CLOCKWISE_PIN[i], GPIO.OUT)

        GPIO.output(ENABLE_PINS[i], True)

        pads[i] = GPIO.PWM(CLOCKWISE_PIN[i], 50)
        pads[i].start(100)

    set_all_intensities([100])


def set_pad_intensity(pad, intensity):
    global pads

    intensities[pad] = int(intensity)

    if pads[pad] is not None:
        pads[pad].ChangeDutyCycle(int(intensities[pad]))


def set_all_intensities(values):
    for i in range(len(pads)):
        val = max(min(values[i], 100), 0)
        set_pad_intensity(i, val)


def get_pad_intensity(pad):
    return intensities[pad]


def close():
    for i in range(len(ENABLE_PINS)):
        GPIO.output(ENABLE_PINS[i], False)
        GPIO.output(CLOCKWISE_PIN[i], False)

    GPIO.cleanup()
