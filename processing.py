import sys
import time
from threading import Thread

import device_io as io
import gui
# import sensor_driver as sd
import motor_driver as vpd
import sensor_sim as sd

AVG_WINDOW_SIZE = 10    # Number of previous polls to be averaged when calculating change rate.
MAX_SENSOR_VAL = 250    # Maximum value that the sensor should produce.
NUM_OF_SENSORS = 6      # Number of Sensors attached to the Nomad device.
POLL_TIME = 0.36        # Time between each poll being made by the sensor, in seconds.
OUTLIER_BUFFER = 500 * POLL_TIME    # Buffer zone around the previous value that is considered non-outlier
REMINDER_TIME = 60      # Number of seconds between reminding about low battery or faulty sensors
MAX_FAULT_RATE = 10

output_mode = 0     # 0 = Standard  1 = Silent  2 = Fancy   3 = GUI
poll_count = 0
prev_values = [None] * AVG_WINDOW_SIZE  # Array of the most recent polls made. For usage in calculating change rate.
last_index = -1     # Index of the last poll added
curr_index = 0      # The index of the oldest poll in the prev_values array
last_outlier = None
next_remind_time = 0

# === Weights for a 6 sensor version ===
left_weights = [1.0, 0.5, 0,
                1.0, 0.5, 0]
centre_weights = [0.5, 1.0, 0.5,
                  0.5, 1.0, 0.5]
right_weights = [0, 0.5, 1.0,
                 0, 0.5, 1.0]

# Array for storing whether a sensor is faulty
faulty_sensors = [False] * NUM_OF_SENSORS
fault_rates = [0] * NUM_OF_SENSORS

faulty_sensor = False
low_battery = False
mute = False


def main():
    global output_mode, gui_class

    if len(sys.argv) > 1 and sys.argv[1] == '-o' and len(sys.argv) > 2:
        if sys.argv[2] == 'none':
            output_mode = 1
        elif sys.argv[2] == 'fancy':
            output_mode = 2
        elif sys.argv[2] == 'gui':
            output_mode = 3
            back_process = Thread(target=run_loop)
            gui_class = gui.gui(io, 600, 300)

            try:
                back_process.start()
                gui_class.run_gui()
            except KeyboardInterrupt:
                if output_mode != 1:
                    print 'Interrupted by User'
                vpd.close()
                sd.close()
                io.close()

            return

    try:
        run_loop()
    except KeyboardInterrupt:
        if output_mode != 1:
            print 'Interrupted by User'
        vpd.close()
        sd.close()
        io.close()


# Represents the core loop of the program, getting sensor data, removing outliers, classifying the results,
# then setting the intensity of the sensors appropriately.
def run_loop():
    global poll_count, next_remind_time, mute, faulty_sensors, faulty_sensor

    io.setup()
    sd.setup_sensors(POLL_TIME / NUM_OF_SENSORS)
    vpd.setup()

    vpd.startup_sequence()
    time.sleep(3)

    # Loops until the user exits.
    while not io.has_requested_exit():
        mute = io.has_requested_mute()
        if mute:
            vpd.set_all_intensities([0, 0, 0])

        if time.time() >= next_remind_time:
            if faulty_sensor:
                for i in range(len(faulty_sensors)):
                    if faulty_sensors[i]:
                        vpd.faulty_sensor_sequence(i)

            if low_battery:
                vpd.low_battery_sequence()

            next_remind_time = time.time() + REMINDER_TIME

        # Store the current time so we know when to poll next.
        last_time = time.time()

        # Get the inputs and normalise them.
        inputs = sd.poll_sensors()
        poll_count += 1

        inputs = check_faulty_values(inputs)

        if inputs is None:
            for i in range(NUM_OF_SENSORS):
                if faulty_sensors[i]:
                    vpd.faulty_sensor_sequence(i)

            continue

        for i in range(len(inputs)):
            inputs[i] = max(min(inputs[i], MAX_SENSOR_VAL), 0)

        # Check if the inputs are an outlier, if they aren't then set the outputs appropriately.
        if not is_outlier(inputs):
            results = calc_output(inputs)
            intensities = results[:3]

            if not mute:
                vpd.set_all_intensities(intensities)

            if output_mode == 3:
                gui_class.set_values(inputs, intensities, results[3])
        elif output_mode != 1:
            print("Outlier: {}".format(inputs))

        # Wait until the next step is reached.
        while time.time() < last_time + POLL_TIME:
            time.sleep(0.01)

    vpd.close()
    sd.close()
    io.close()


def check_faulty_values(values):
    global faulty_sensors, faulty_sensor, fault_rates

    for i in range(NUM_OF_SENSORS):
        if faulty_sensors[i]:
            continue

        if values[i] < 1 or (MAX_SENSOR_VAL + 50 < values[i] < 2220) or values[i] > 2280:
            if output_mode != 1:
                print '{} is a faulty value at sensor {}'.format(values[i], i)

            fault_rates[i] += 1
        else:
            fault_rates[i] -= 1. / 5

        if fault_rates[i] > MAX_FAULT_RATE:
            if output_mode != 1:
                print 'Faulty Sensor {} Detected'.format(i)

            faulty_sensors[i] = True
            faulty_sensor = True

    if sum(faulty_sensors) == 1:
        for i in    range(NUM_OF_SENSORS):
            if faulty_sensors[i]:
                values = interpolate_value(values, i)
    elif sum(faulty_sensors) > 1:
        return None

    return values


def interpolate_value(inputs, i):
    total = 0
    count = 0

    if i - 3 >= 0:
        total += inputs[i - 3]
        count += 1

    if i + 3 < NUM_OF_SENSORS:
        total += inputs[i + 3]
        count += 1

    if int((i - 1) / 3) == int(i / 3):
        total += inputs[i - 1]
        count += 1

    if int((i + 1) / 3) == int(i / 3):
        total += inputs[i + 1]
        count += 1

    inputs[i] = total / count

    if output_mode != 1:
        print 'Sensor {} value interpolated to {}'.format(i, inputs[i])

    return inputs


def is_outlier(inputs):
    global last_outlier

    if last_index == -1:
        return False

    for i in range(len(inputs)):
        prev = prev_values[last_index][i]

        if prev == MAX_SENSOR_VAL or inputs[i] == MAX_SENSOR_VAL:
            continue

        if abs(inputs[i] - prev) > OUTLIER_BUFFER:
            if last_outlier is not None:
                if sum([abs(a - b) for a, b in zip(inputs, last_outlier)]) / NUM_OF_SENSORS <= OUTLIER_BUFFER:
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

    closeness = [MAX_SENSOR_VAL - i for i in inputs]

    # Calculate the weighted average distance for each output.
    left_avg_closeness = get_weighted_average(closeness, left_weights, 1)
    centre_avg_closeness = get_weighted_average(closeness, centre_weights, 1)
    right_avg_closeness = get_weighted_average(closeness, right_weights, 1)

    # Calculate the change rates for each sensor
    left_change = get_weighted_average(normalised_change, left_weights, 1)
    centre_change = get_weighted_average(normalised_change, centre_weights, 1)
    right_change = get_weighted_average(normalised_change, right_weights, 1)

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
# Larger values should represent sudden, large movements.
def calc_change_magnitude(values):
    # Calculate the total distance, across the last few polls, at each sensor.
    totals = [0] * NUM_OF_SENSORS
    for i in range(len(prev_values)):
        if prev_values[i] is None:
            continue

        for j in range(len(totals)):
            totals[j] += prev_values[i][j]

    return [abs((t / AVG_WINDOW_SIZE) - v) / MAX_SENSOR_VAL for t, v in zip(totals, values)]


# Use the weight arrays to calculate a weighted average distance for a particular output.
def get_weighted_average(values, weights, output):
    avgs = []
    for i in range(len(values)):
        avgs.append(values[i] * weights[i])

    if output == 1:
        return max(avgs)
    else:
        return sum(avgs) / sum(weights)


# If this script is being run directly then call the main function
if __name__ == '__main__':
    main()
