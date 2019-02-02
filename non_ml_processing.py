import device_io as io
import sensor_driver as sd
import vibrating_pad_driver as vpd

NUM_OF_POLLS = 100
AVG_WINDOW_SIZE = 10

poll_count = 0

leftWeights = [1.5, 1.0, 0.0,
               2.5, 1.5, 0.0,
               1.5, 1.0, 0.0]

centreWeights = [0.50, 1.25, 0.50,
                 1.25, 2.00, 1.25,
                 0.50, 1.25, 0.50]

rightWeights = [0.0, 1.0, 1.5,
                0.0, 1.5, 2.5,
                0.0, 1.0, 1.5]


# Represents the core loop of the program, getting sensor data, removing outliers, classifying the results,
# then setting the intensity of the sensors appropriately
def main():
    global poll_count
    sd.setup_sensors()

    count = 0
    while not io.has_requested_exit():
        inputs = sd.poll_sensors()
        poll_count += 1

        if not is_outlier(inputs):
            intensities = calc_output(inputs)
            vpd.set_all_intensities(intensities)

        count += 1
        if count > NUM_OF_POLLS - 1:
            io.request_exit()


def is_outlier(inputs):
    return False


prev_values = [None] * AVG_WINDOW_SIZE
last_index = 0


def calc_output(inputs):
    global prev_values, last_index

    change = calc_change_magnitude(inputs)
    normalised_change = (-1 / (1 + 10000 * (pow(100000, change - 1)))) + 1

    prev_values[last_index] = inputs
    last_index = (last_index + 1) % AVG_WINDOW_SIZE

    left_avg = get_weighted_average(inputs, leftWeights)
    centre_avg = get_weighted_average(inputs, centreWeights)
    right_avg = get_weighted_average(inputs, rightWeights)

    left_intensity = normalised_change * ((500 - left_avg) / 5)
    centre_intensity = normalised_change * ((500 - centre_avg) / 5)
    right_intensity = normalised_change * ((500 - right_avg) / 5)

    print("{}\t{}\t{}".format(left_intensity, centre_intensity, right_intensity))
    return left_intensity, centre_intensity, right_intensity


def calc_change_magnitude(values):
    totals = [0] * 9
    for i in range(len(prev_values)):
        if prev_values[i] is None:
            continue

        for j in range(len(totals)):
            totals[j] += prev_values[i][j]

    total_diff = 0
    for i in range(len(totals)):
        total_diff += abs((totals[i] / 9) - values[i])

    return (total_diff / len(totals)) / 500


def get_weighted_average(values, weights):
    total = 0
    for i in range(len(values)):
        total += values[i] * weights[i]

    return total / sum(weights)


if __name__ == '__main__':
    main()
