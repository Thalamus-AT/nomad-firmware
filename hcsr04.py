# Test for HC-SR04 ultrasonic distance sensor
# Make sure to run as sudo!

import time

import RPi.GPIO as GPIO

TRIG = [23, 19] # output pin
ECHO = [24, 20] # input pin


def setup_sensors():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    GPIO.output(TRIG, False) # set output pin low
    time.sleep(3) # allow time for sensor to settle


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
    while GPIO.input(ECHO[num]) == 0:
        start_time = time.time()
    while GPIO.input(ECHO[num]) == 1:
        end_time = time.time()

    pulse_time = end_time - start_time

    # Calculate distance using S = D / T. Assume speed of sound is 343m/s (at sea level)
    distance = (pulse_time * 343) / 2 # halve for distance to object
    # print "Distance:", distance, "m"

    return distance * 100


def close():
    GPIO.cleanup()
