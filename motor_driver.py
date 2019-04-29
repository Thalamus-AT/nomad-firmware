import os
import time

# Check the system we are running on, if it is 64 bit we can presume it isn't the Pi
if os.uname()[4] == 'x86_64':
    import GPIO_Sim as GPIO
else:
    import RPi.GPIO as GPIO

STARTUP_FADEIN_SPEED = 6    # Speed that the vibrating motors fade in on startup.
STARTUP_FADEOUT_SPEED = 6   # Speed that the vibrating motors fade out on startup.
LOW_BATTERY_PULSES = 2      # Number of pulses used to signify a low battery.
FAULTY_BIG_PULSES = 3       # Number of pulses used to signify a faulty sensor.

# intensities = array.array('I', [0, 0, 0])
intensities = [0] * 3   # List for storing the intensity values.

ENABLE_PINS = [4, 4, 4]             # The pins used to enable each motor.
CLOCKWISE_PIN = [10, 11, 9]         # The pins used to set the intensity of the motors.
motors = [None] * len(ENABLE_PINS)    # The objects used to set the PWM values for each motor.


# Sets up the relevant GPIO pins.
def setup():
    global motors

    # Iterate through each of the motors.
    for i in range(len(ENABLE_PINS)):
        # Setup the relevant pins for usage.
        GPIO.setup(ENABLE_PINS[i], GPIO.OUT)
        GPIO.setup(CLOCKWISE_PIN[i], GPIO.OUT)

        # Enable the motor.
        GPIO.output(ENABLE_PINS[i], True)

        # Create the PWM objects for controlling the motor intensities.
        motors[i] = GPIO.PWM(CLOCKWISE_PIN[i], 50)
        motors[i].start(100)


# Set the intensity of an individual motor.
def set_motor_intensity(motor, intensity):
    global motors

    # Assert that the PWM object has been initialised.
    assert motors[motor] is not None

    # Convert the value to an integer.
    intensities[motor] = max(min(int(intensity), 100), 0)

    # Set the new intensity.
    motors[motor].ChangeDutyCycle(int(intensities[motor]))


# Set the intensity for all the motors.
def set_all_intensities(values):
    for i, val in enumerate(values):
        set_motor_intensity(i, val)


# Return the intensity of a motor.
def get_pad_intensity(motor):
    return intensities[motor]


# Disable all the motors and cleanup the GPIO ports.
def close():
    for i in range(len(ENABLE_PINS)):
        GPIO.output(ENABLE_PINS[i], False)
        GPIO.output(CLOCKWISE_PIN[i], False)

    GPIO.cleanup()


# Perform the sequence to inform the user that the device is starting.
def startup_sequence():
    # Fade the motors in
    i = 0
    while i <= 100:
        set_all_intensities([i, i, i])
        i += STARTUP_FADEIN_SPEED
        time.sleep(0.1)

    # Fade the motors out
    i = 100
    while i >= 0:
        set_all_intensities([i, i, i])
        i -= STARTUP_FADEOUT_SPEED
        time.sleep(0.1)


# Perform the sequence to inform the user that the device is low on battery.
def low_battery_sequence():
    # Pause all feedback
    set_all_intensities([0, 0, 0])
    time.sleep(0.4)

    # Perform the pulses.
    for i in range(LOW_BATTERY_PULSES):
        set_all_intensities([100, 100, 100])
        time.sleep(0.2)
        set_all_intensities([0, 0, 0])
        time.sleep(0.2)

    time.sleep(0.2)


# Perform the sequence to inform the user that a sensor is faulty.
def faulty_sensor_sequence(sensor):
    # Determine which side the sensor is on.
    motor = sensor % 3

    # Determine if the sensor is on the top row.
    top = sensor < 3

    # Pause all feedback
    set_all_intensities([0, 0, 0])
    time.sleep(0.4)

    # Perform the big pulses.
    for i in range(FAULTY_BIG_PULSES):
        set_all_intensities([100, 100, 100])
        time.sleep(0.2)
        set_all_intensities([0, 0, 0])
        time.sleep(0.2)

    # Perform two pulses with the motor on the same side as the faulty sensor.
    for i in range(2):
        set_motor_intensity(motor, 100)
        time.sleep(0.2)
        set_motor_intensity(motor, 0)
        time.sleep(0.2)

    # Perform another pulse on the same side if the sensor is on the top row.
    if top:
        set_motor_intensity(motor, 100)
        time.sleep(0.2)
        set_motor_intensity(motor, 0)

    time.sleep(0.4)
