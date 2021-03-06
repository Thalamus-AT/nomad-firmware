import os
import time

# Check the system we are running on, if it is 64 bit we can presume it isn't the Pi
if os.uname()[4] == 'x86_64':
    import GPIO_Sim as GPIO
else:
    import RPi.GPIO as GPIO

TRIG = [23, 25, 16, 21, 17,  6]  # Output pins for each sensor.
ECHO = [24, 12, 20,  2,  5, 13]  # Input pins for each sensor.
period = 0.025


# Setup all the required GPIO pins.
def setup_sensors(p):
    global period

    # Assert that the duration assigned to each sensor is long enough.
    assert p >= period
    period = p

    # Setup the trigger and echo pins.
    for t in TRIG:
        GPIO.setup(t, GPIO.OUT)
    for e in ECHO:
        GPIO.setup(e, GPIO.IN)

    # Set output pin low then allow time to settle
    GPIO.output(TRIG, False)
    time.sleep(2)


# Poll all the sensors in sequence.
def poll_sensors():
    results = []
    for i in range(len(TRIG)):
        # Poll the sensor.
        start_time = time.time()
        results.append(poll_sensor(i))

        # Wait until the assigned duration has been completed. This prevents the sensors interfering.
        while time.time() < (start_time + period):
            time.sleep(0.005)

    return results


# Poll and individual sensor.
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


# Cleanup the GPIO pins that were used.
def close():
    GPIO.cleanup()
