import os

# Check the system we are running on, if it is 64 bit we can presume it isn't the Pi
if os.uname()[4] == 'x86_64':
    import GPIO_Sim as GPIO
else:
    import RPi.GPIO as GPIO

SLEEP_PIN = 26

requested_exit = False
mute = False
prev_mute_val = 1


def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SLEEP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Called when the user wants to exit
def request_exit():
    global requested_exit
    requested_exit = True


# Called by the main loop to check whether to exit
def has_requested_exit():
    return requested_exit


def has_requested_mute():
    global mute, prev_mute_val

    if not GPIO.input(SLEEP_PIN):
        if prev_mute_val != 0:
            print('Sleep Button Pressed')
            mute = not mute

        prev_mute_val = 0
    else:
        prev_mute_val = 1

    return mute


def close():
    GPIO.cleanup()
