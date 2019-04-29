import os

# Check the system we are running on, if it is 64 bit we can presume it isn't the Pi
if os.uname()[4] == 'x86_64':
    import GPIO_Sim as GPIO
else:
    import RPi.GPIO as GPIO

MUTE_PIN = 26           # The pin attached to the mute button.
LOW_BATTERY_PIN = 19    # The pin attached to the low-battery signal.

requested_exit = False  # Whether the user has requested exit from the program
mute = False            # Whether the device is muted.
prev_mute_val = 1       # What the previous value from the mute button was.


# Setup the relevant GPIO pins.
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MUTE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LOW_BATTERY_PIN, GPIO.IN)


# Called when the user wants to exit
def request_exit():
    global requested_exit
    requested_exit = True


# Called by the main loop to check whether to exit
def has_requested_exit():
    return requested_exit


# Checks the mute button to see if they have attempted to mute the device.
def has_requested_mute():
    global mute, prev_mute_val

    # When the mute button is first depressed then toggle the mute value.
    if not GPIO.input(MUTE_PIN):
        if prev_mute_val != 0:
            print('Sleep Button Pressed')
            mute = not mute

        prev_mute_val = 0
    else:
        prev_mute_val = 1

    return mute


# Checks if the battery is low on charge.
def is_battery_low():
    return not GPIO.input(LOW_BATTERY_PIN)


# Cleans up the GPIO pins.
def close():
    GPIO.cleanup()
