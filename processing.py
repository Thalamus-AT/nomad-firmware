import sys
import time
from threading import Thread

import device_io as io
import gui
# import sensor_sim as sd
import motor_driver as vpd
import sensor_driver as sd

AVG_WINDOW_SIZE = 10    # Number of previous polls to be averaged when calculating change rate.
MAX_SENSOR_VAL = 250    # Maximum value that the sensor should produce.
NUM_OF_SENSORS = 6      # Number of Sensors attached to the Nomad device.
POLL_TIME = 0.2         # Duration, in seconds, that is allowed for all sensors to be polled.
REMINDER_TIME = 60      # Number of seconds between reminding about low battery or faulty sensors.
MAX_FAULT_RATE = 10     # The fault rate value that a sensor must reach or exceed to be considered faulty.
OUTLIER_BUFFER = 500 * POLL_TIME    # Buffer zone around the previous value that is considered non-outlier. Equivalent
                                    # to the distance that an object moving at 5m/s can move between polls.

output_mode = 0         # 0 = Standard  1 = Silent  2 = Fancy   3 = GUI
poll_count = 0          # Tracks the number of polls that have occurred
last_outlier = None     # Contains the last array of values to be classified as an outlier
next_remind_time = 0    # Contains the next time when the user needs to be reminded about low battery or faulty sensors.

prev_values = [None] * AVG_WINDOW_SIZE  # Array of the most recent polls made. For usage in calculating change rate.
last_index = -1     # Index of the last poll added to the prev_values array.
curr_index = 0      # The index of the oldest poll in the prev_values array.

faulty_sensors = [False] * NUM_OF_SENSORS   # Array containing whether each sensor is faulty.
fault_rates = [0] * NUM_OF_SENSORS          # Array containing the fault rate for each sensor.

mute = False    # Stores whether the device is currently muted.

# Weights for a 6 sensors
left_weights = [1.0, 0.5, 0,
                1.0, 0.5, 0]

centre_weights = [0.5, 1.0, 0.5,
                  0.5, 1.0, 0.5]

right_weights = [0.0, 0.5, 1.0,
                 0.0, 0.5, 1.0]


# The main function is where the firmware starts. It checks for command line arguments, starts the GUI if relevant, and
# starts the core loop.
def main():
    global output_mode, gui_class

    # Check if there are any command line arguments of the correct format.
    if len(sys.argv) > 1 and sys.argv[1] == '-o' and len(sys.argv) > 2:
        # Set the output mode according to the argument.
        if sys.argv[2] == 'none':
            output_mode = 1
        elif sys.argv[2] == 'fancy':
            output_mode = 2
        elif sys.argv[2] == 'gui':
            output_mode = 3

            # If we are using a GUI, then set up the GUI on the main thread, and run the core loop on a separate thread.
            back_process = Thread(target=run_loop)
            gui_class = gui.gui(io, 600, 300)

            try:
                back_process.start()
                gui_class.run_gui()
            except KeyboardInterrupt:
                handle_interrupt()

            return

    # Run the core loop on the main thread, if we aren't using a GUI.
    try:
        run_loop()
    except KeyboardInterrupt:
        handle_interrupt()


# Called when the program is interrupted. Cleans up the GPIO pins and anything else that is necessary before shutdown.
def handle_interrupt():
    if output_mode != 1:
        print 'Interrupted by User'

    vpd.close()
    sd.close()
    io.close()


# Represents the core loop of the program, getting sensor data, removing outliers, classifying the results,
# then setting the intensity of the sensors appropriately.
def run_loop():
    global poll_count, next_remind_time, mute, faulty_sensors

    # Set up all the IO.
    io.setup()
    sd.setup_sensors(POLL_TIME / NUM_OF_SENSORS)
    vpd.setup()

    # Perform the startup sequence and add a short wait.
    vpd.startup_sequence()
    time.sleep(1)

    # Loops until the user exits, or it is interrupted.
    while not io.has_requested_exit():
        # Check if the user has requested a mute, and perform the mute if they have.
        mute = io.has_requested_mute()
        if mute:
            vpd.set_all_intensities([0, 0, 0])

        # Check if it is time to the remind the user of any outstanding situations (low battery/faulty sensor)
        if time.time() >= next_remind_time:
            # Perform the faulty sensor sequence for any sensors that have been classified as faulty.
            for i in range(len(faulty_sensors)):
                if faulty_sensors[i]:
                    vpd.faulty_sensor_sequence(i)

            # Perform the low battery sequence if the battery is low.
            if io.is_battery_low():
                vpd.low_battery_sequence()

            # Calculate the time to remind the user next.
            next_remind_time = time.time() + REMINDER_TIME

        # Store the current time so we know when to poll next.
        # last_time = time.time()

        # Get the inputs by polling the sensors.
        inputs = sd.poll_sensors()
        poll_count += 1

        # Check the raw sensor values for faulty values.
        inputs = check_faulty_values(inputs)

        # Check if more than two sensors have been classified as faulty.
        if inputs is None:
            # Perform the faulty sensor sequence for all faulty sensors.
            for i in range(NUM_OF_SENSORS):
                if faulty_sensors[i]:
                    vpd.faulty_sensor_sequence(i)

            # Skip to the next loop iteration. This effectively causes the faulty sensor signals to be repeated.
            continue

        # Clip the raw input values to the range 0 - MAX_SENSOR_VAL
        for i in range(len(inputs)):
            inputs[i] = max(min(inputs[i], MAX_SENSOR_VAL), 0)

        # Check if the inputs are an outlier, if they aren't then set the outputs appropriately.
        if not is_outlier(inputs):
            # Calculate the vibration intensities from the sensor values.
            results = calc_output(inputs)
            intensities = results[:3]

            # Set the motors to the calculated intensities provided the device is not muted.
            if not mute:
                vpd.set_all_intensities(intensities)

            # Update the values in the GUI if relevant.
            if output_mode == 3:
                gui_class.set_values(inputs, intensities, results[3])
        elif output_mode != 1:
            print("Outlier: {}".format(inputs))

        # Wait until the next step is reached.
        # while time.time() < last_time + POLL_TIME:
        #     time.sleep(0.01)

    # Cleanup and stop the device.
    vpd.close()
    sd.close()
    io.close()


# Given the raw sensor values, the function determines if any of them are faulty, if a sensor can be considered faulty,
# and interpolates the value for faulty sensors.
def check_faulty_values(values):
    global faulty_sensors, fault_rates

    # Loop through each sensor value.
    for i in range(NUM_OF_SENSORS):
        # If the sensor is already classified as faulty then we can ignore its values.
        if faulty_sensors[i]:
            continue

        # If the value is outside the normal range then it is considered faulty.
        if values[i] < 1 or (MAX_SENSOR_VAL + 50 < values[i] < 2100) or values[i] > 2500:
            if output_mode != 1:
                print '{} is a faulty value at sensor {}'.format(values[i], i)

            # Increment the fault rate for this sensor.
            fault_rates[i] += 1
        else:
            # Decrease the fault rate for this sensor, if the value isn't faulty.
            fault_rates[i] = max(fault_rates[i] - 1. / 5, 0)

        # If the sensor has equalled or exceeded the MAX_FAULT_RATE then it is classified as faulty
        if fault_rates[i] >= MAX_FAULT_RATE:
            if output_mode != 1:
                print 'Faulty Sensor {} Detected'.format(i)

            faulty_sensors[i] = True

    # Check how many faulty sensors there are.
    if sum(faulty_sensors) == 1:
        # If there is only one faulty sensor then interpolate its value.
        for i in range(NUM_OF_SENSORS):
            if faulty_sensors[i]:
                values = interpolate_value(values, i)
    elif sum(faulty_sensors) > 1:
        # If there are multiple faulty sensors then return None. signalling that normal functionality should halt.
        return None

    return values


# Replaces a faulty value with a value interpolated from the surrounding values.
def interpolate_value(inputs, i):
    total = 0
    count = 0

    # Check the value above.
    if i - 3 >= 0:
        total += inputs[i - 3]
        count += 1

    # Check the value below.
    if i + 3 < NUM_OF_SENSORS:
        total += inputs[i + 3]
        count += 1

    # Check the value to the left.
    if int((i - 1) / 3) == int(i / 3):
        total += inputs[i - 1]
        count += 1

    # Check the value to the right.
    if int((i + 1) / 3) == int(i / 3):
        total += inputs[i + 1]
        count += 1

    # Calculate the interpolated value.
    inputs[i] = total / count

    if output_mode != 1:
        print 'Sensor {} value interpolated to {}'.format(i, inputs[i])

    return inputs


# Checks if a set of values can be considered as outliers.
def is_outlier(inputs):
    global last_outlier

    # If this is the first value then we consider it not an outlier by default.
    if last_index == -1:
        return False

    # Iterate through all the sensors.
    for i in range(NUM_OF_SENSORS):

        # Get the previous value at this sensor.
        prev = prev_values[last_index][i]

        # If the sensor has just moved to or from the max value then don't consider it an outlier.
        if prev == MAX_SENSOR_VAL or inputs[i] == MAX_SENSOR_VAL:
            continue

        # Check if the difference between the current value and the last value exceeds the buffer.
        if abs(inputs[i] - prev) > OUTLIER_BUFFER:
            # Check if the average difference between the current value and the last outlier is less than the buffer.
            if last_outlier is not None:
                if sum([abs(a - b) for a, b in zip(inputs, last_outlier)]) / NUM_OF_SENSORS <= OUTLIER_BUFFER:
                    # Replace the previous value with the outlier, and consider the this value as not an outlier.
                    prev_values[last_index] = last_outlier
                    last_outlier = None
                    return False

            last_outlier = inputs
            return True

    return False


# Calculates the intensity values to be output to the vibrating pads.
def calc_output(inputs):
    global prev_values, last_index, curr_index

    # Get the rate-of-change value and normalise it.
    change = calc_change_magnitude(inputs)
    normalised_change = [(-1 / (1 + 10000 * (pow(100000, c - 1)))) + 1 for c in change]

    # Update the prev_values array.
    prev_values[curr_index] = inputs
    last_index = curr_index
    curr_index = (curr_index + 1) % AVG_WINDOW_SIZE

    # Calculate the closeness values.
    closeness = [MAX_SENSOR_VAL - i for i in inputs]

    # Calculate the weighted average distance for each output.
    left_avg_closeness = get_weighted_average(closeness, left_weights)
    centre_avg_closeness = get_weighted_average(closeness, centre_weights)
    right_avg_closeness = get_weighted_average(closeness, right_weights)

    # Calculate the change rates for each sensor
    left_change = get_weighted_average(normalised_change, left_weights)
    centre_change = get_weighted_average(normalised_change, centre_weights)
    right_change = get_weighted_average(normalised_change, right_weights)

    # Convert the average distances into the intensity value.
    left_intensity = left_change * (left_avg_closeness / (MAX_SENSOR_VAL / 100.))
    centre_intensity = centre_change * (centre_avg_closeness / (MAX_SENSOR_VAL / 100.))
    right_intensity = right_change * (right_avg_closeness / (MAX_SENSOR_VAL / 100.))

    # Print the relevant output.
    if output_mode == 2:
        sys.stdout.write("\rIntensities: {} \t{} \t{}".format(left_intensity, centre_intensity, right_intensity))
        sys.stdout.flush()
    elif output_mode == 0:
        print("Intensities: {} \t{} \t{}".format(left_intensity, centre_intensity, right_intensity))

    return left_intensity, centre_intensity, right_intensity, normalised_change


# Calculates the magnitude of change between the last few values and the current values.
# Larger values represent sudden, large movements.
def calc_change_magnitude(values):
    # Calculate the total distance, across the last few polls, at each sensor.
    totals = [0] * NUM_OF_SENSORS
    for i in range(len(prev_values)):
        if prev_values[i] is None:
            continue

        for j in range(len(totals)):
            totals[j] += prev_values[i][j]

    # Return the differences between the average of the last few values and the current value, at each sensor.
    return [abs((t / AVG_WINDOW_SIZE) - v) / MAX_SENSOR_VAL for t, v in zip(totals, values)]


# Use the weight arrays to calculate a weighted average distance for a particular output.
def get_weighted_average(values, weights):
    # Calculate all the weighted values.
    avgs = []
    for i in range(NUM_OF_SENSORS):
        avgs.append(values[i] * weights[i])

    # Return the maximum of these values, meaning the closest.
    return max(avgs)


# If this script is being run directly then call the main function
if __name__ == '__main__':
    main()
