
# =====================================================
#
#   This script is currently unused and out of date.
#   For the current version see 'processing.py'
#
# =====================================================

# from sklearn.cluster import DBSCAN
import time

import device_io as io
import motor_driver as vpd
# import sensor_driver as sd
import sensor_driver as sd

MAX_SENSOR_DISTANCE = 300
DBS_MAX_DISTANCE = 200
DBS_MIN_SAMPLES = 2
NON_OUTLIER_COUNT = 50
NUM_OF_POLLS = 99

POLL_TIME = 0.5

valid_data_points = []
poll_count = 0
model = None


# Represents the core loop of the program, getting sensor data, removing outliers, classifying the results,
# then setting the intensity of the sensors appropriately
def main():
    global poll_count
    sd.setup_sensors()
    vpd.setup()

    count = 0
    while not io.has_requested_exit():
        last_time = time.time()
        inputs = sd.poll_sensors()
        poll_count += 1
        print inputs
        while time.time() < last_time + POLL_TIME:
            time.sleep(0.01)

        # if not is_outlier(inputs):
        #     class_num = classify_inputs(inputs)
        #     output_by_class(class_num, 100)
        #
        # count += 1
        # if count > NUM_OF_POLLS - 1:
        #     io.request_exit()

    sd.close()

    print
    print "Results:"
    print "  {} polls made".format(poll_count)
    print "  {} non-outlier polls".format(len(valid_data_points))
    print "  Resulting labels are {}".format(list(set(model.labels_)))


# Uses DBSCAN to determine if a sensor reading is an outlier
def is_outlier(inputs):
    global valid_data_points, poll_count, model

    # This run on the first loop to setup the initial model
    if model is None:
        print "Initialising Model"
        model = DBSCAN(DBS_MAX_DISTANCE, DBS_MIN_SAMPLES)
        valid_data_points = [inputs]
        model.fit(valid_data_points)
        print "Poll 1 added to valid points (class {})".format(model.labels_[0])
        return False

    # Predict the label of the new data point
    label = model.fit_predict(valid_data_points + [inputs])[len(valid_data_points)]

    # If the label does not indicate an outlier or if it is one of the initial few points it is added to the data
    if label != -1 or poll_count <= NON_OUTLIER_COUNT:
        print "Poll {} added to valid points (class {})".format(poll_count, label)
        valid_data_points = valid_data_points + [inputs]
    else:
        print "Poll {} classified as an outlier (class {})".format(poll_count, label)

    # The model is fit to whatever points are deemed valid
    model.fit(valid_data_points)

    return label == -1 and poll_count > NON_OUTLIER_COUNT


# def is_outlier(inputs):
#     global valid_data_points, poll_count, model
#
#     if model is None:
#         model = DBSCAN(DBS_MAX_DISTANCE, DBS_MIN_SAMPLES)
#         valid_data_points = [inputs]
#         model.fit(valid_data_points)
#         return False
#
#     valid_data_points = valid_data_points + [inputs]
#     label = model.fit_predict(valid_data_points)[len(valid_data_points) - 1]
#     print "Poll {} given class {}".format(poll_count, label)
#
#     return label == -1


# Will classify the points using k-means to determine the type of obstacle
def classify_inputs(inputs):
    # K-MEANS
    return 1


# Based on the class determined previously the function will define an appropriate response via the vibrating pads
def output_by_class(class_num, distance):
    if class_num == 0:
        # print "Obstacle on the LEFT"
        vpd.set_pad_intensity(0, (1 - (distance / MAX_SENSOR_DISTANCE)) * 100)
    elif class_num == 1:
        # print "Obstacle in FRONT"
        vpd.set_pad_intensity(0, (1 - (distance / MAX_SENSOR_DISTANCE)) * 100)
        vpd.set_pad_intensity(1, (1 - (distance / MAX_SENSOR_DISTANCE)) * 100)
    elif class_num == 2:
        # print "Obstacle on the RIGHT"
        vpd.set_pad_intensity(1, (1 - (distance / MAX_SENSOR_DISTANCE)) * 100)


main()
