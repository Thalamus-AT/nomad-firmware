import os
import time

# Check the system we are running on, if it is 64 bit we can presume it isn't the Pi
if os.uname()[4] == 'x86_64':
    import GPIO_Sim as GPIO
else:
    import RPi.GPIO as GPIO

TRIG = [23, 25, 16, 21, 17, 6]  # Output pins
ECHO = [24, 12, 20, 3, 5, 13]  # Input pins


def setup_sensors():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for t in TRIG:
        GPIO.setup(t, GPIO.OUT)
    for e in ECHO:
        GPIO.setup(e, GPIO.IN)

    # Set output pin low then allow time to settle
    GPIO.output(TRIG, False)
    time.sleep(3)


def poll_sensors():
    results = []
    for i in range(len(TRIG)):
        results.append(poll_sensor(i))

    return results


def poll_sensor(num):
    # Send a 10us pulse to trigger the sensor to send 8 x 40kHz bursts
    GPIO.output(TRIG[num], True)
    time.sleep(0.00001)
    GPIO.output(TRIG[num], False)

    # Calculate time between on and off signals
    start_time = time.time()
    while GPIO.input(ECHO[num]) == 0:
        start_time = time.time()

    end_time = time.time()
    while GPIO.input(ECHO[num]) == 1:
        end_time = time.time()

    pulse_time = end_time - start_time

    # Calculate distance using S = D / T. Assume speed of sound is 343m/s (at sea level). Then half for just the
    # to the object.
    distance = (pulse_time * 343) / 2
    return distance * 100


def close():
    GPIO.cleanup()
