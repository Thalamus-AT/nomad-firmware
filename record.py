import sys
import time

import sensor_driver as sd

POLL_TIME = 0.2
MAX_SENSOR_VAL = 250
AVG_WINDOW_SIZE = 10
NUM_OF_SENSORS = 6

# === Weights for a 6 sensor version ===
left_weights = [1.0, 0.5, 0,
                1.0, 0.5, 0]
centre_weights = [0.5, 1.0, 0.5,
                  0.5, 1.0, 0.5]
right_weights = [0, 0.5, 1.0,
                 0, 0.5, 1.0]

output_mode = 1


def main():
    filename = time.strftime('%Y-%m-%d--%H-%M-%S') + '.data'
    print('File: {}'.format(filename))

    sd.setup_sensors()

    while True:
        # Store the current time so we know when to poll next.
        last_time = time.time()

        inputs = sd.poll_sensors()
        with open('data/' + filename, 'a') as f:
            print(inputs)
            f.write(','.join([str(i) for i in inputs]))
            outs = calc_output(inputs)[:3]
            f.write(',' + ','.join([str(i) for i in outs]))

        # Wait until the next step is reached.
        while time.time() < last_time + POLL_TIME:
            time.sleep(0.01)

    sd.close()


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

if __name__ == '__main__':
    main()
