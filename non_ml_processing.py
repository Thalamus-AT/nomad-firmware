import time

import device_io as io
# import sensor_driver as sd
import hcsr04 as sd
import vibrating_pad_driver as vpd

NUM_OF_POLLS = 100
AVG_WINDOW_SIZE = 10

poll_count = 0

MAX_SENSOR_VAL = 200
NUM_OF_SENSORS = 2
POLL_TIME = 0.2

# left_weights = [1.5, 1.0, 0.0,
#                2.5, 1.5, 0.0,
#                1.5, 1.0, 0.0]
#
# centre_weights = [0.50, 1.25, 0.50,
#                  1.25, 2.00, 1.25,
#                  0.50, 1.25, 0.50]
#
# right_weights = [0.0, 1.0, 1.5,
#                 0.0, 1.5, 2.5,
#                 0.0, 1.0, 1.5]

left_weights = [1.0, 0.0]

centre_weights = [1.0, 1.0]

right_weights = [0.0, 1.0]


# Represents the core loop of the program, getting sensor data, removing outliers, classifying the results,
# then setting the intensity of the sensors appropriately
def main():
    global poll_count
    sd.setup_sensors()
    vpd.setup()

    while not io.has_requested_exit():
        last_time = time.time()
        inputs = sd.poll_sensors()
        for i in range(len(inputs)):
            inputs[i] = min(inputs[i], MAX_SENSOR_VAL)

        poll_count += 1

        # print inputs
        while time.time() < last_time + POLL_TIME:
            time.sleep(0.01)

        if not is_outlier(inputs):
            intensities = calc_output(inputs)
            vpd.set_all_intensities(intensities)

        # if poll_count > NUM_OF_POLLS - 1:
        #     io.request_exit()

    sd.close()
    vpd.close()


def is_outlier(inputs):
    return False


prev_values = [None] * AVG_WINDOW_SIZE
last_index = 0


def calc_output(inputs):
    global prev_values, last_index

    change = calc_change_magnitude(inputs)
    normalised_change = (-1 / (1 + 10000 * (pow(100000, change - 1)))) + 1
    # print("Change: {}".format(change))
    # print("Normalised Change: {}".format(normalised_change))

    prev_values[last_index] = inputs
    last_index = (last_index + 1) % AVG_WINDOW_SIZE

    left_avg = get_weighted_average(inputs, left_weights)
    centre_avg = get_weighted_average(inputs, centre_weights)
    right_avg = get_weighted_average(inputs, right_weights)
    # print("Averages: {}\t{}\t{}".format(left_avg, centre_avg, right_avg))

    left_intensity = normalised_change * ((MAX_SENSOR_VAL - left_avg) / (MAX_SENSOR_VAL / 100))
    centre_intensity = normalised_change * ((MAX_SENSOR_VAL - centre_avg) / (MAX_SENSOR_VAL / 100))
    right_intensity = normalised_change * ((MAX_SENSOR_VAL - right_avg) / (MAX_SENSOR_VAL / 100))

    print("Intensities: {}\t{}\t{}".format(left_intensity, centre_intensity, right_intensity))
    return left_intensity, centre_intensity, right_intensity


def calc_change_magnitude(values):
    totals = [0] * NUM_OF_SENSORS
    for i in range(len(prev_values)):
        if prev_values[i] is None:
            continue

        for j in range(len(totals)):
            totals[j] += prev_values[i][j]

    total_diff = 0
    for i in range(len(totals)):
        total_diff += abs((totals[i] / AVG_WINDOW_SIZE) - values[i])

    return total_diff / MAX_SENSOR_VAL


def get_weighted_average(values, weights):
    total = 0
    for i in range(len(values)):
        total += values[i] * weights[i]

    return total / sum(weights)


if __name__ == '__main__':
    main()
