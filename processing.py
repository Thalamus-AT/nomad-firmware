from sklearn.cluster import DBSCAN

import device_io as io
import sensor_driver as sd
import vibrating_pad_driver as vpd

MAX_SENSOR_DISTANCE = 300
DBS_MAX_DISTANCE = 1000
DBS_MIN_SAMPLES = 2
NON_OUTLIER_COUNT = 4

valid_data_points = []
poll_count = 0
model = None


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
            class_num = classify_inputs(inputs)
            output_by_class(class_num, 100)

        count += 1
        if count > 9:
            io.request_exit()


# Uses DBSCAN to determine if a sensor reading is an outlier
def is_outlier(inputs):
    global valid_data_points, poll_count, model

    print "Sensor Reading is {}".format(inputs)

    # This run on the first loop to setup the initial model
    if model is None:
        print "Initialising Model"
        model = DBSCAN(DBS_MAX_DISTANCE, DBS_MIN_SAMPLES)
        valid_data_points = [inputs]
        model.fit(valid_data_points)
        print "First Data Point Added"
        return False

    # Predict the label of the new data point
    label = model.fit_predict([inputs])

    # If the label does not indicate an outlier or if it is one of the initial few points it is added to the data
    if label != -1 or poll_count <= NON_OUTLIER_COUNT:
        valid_data_points = valid_data_points + [inputs]

    # The model is fit to whatever points are deemed valid
    model.fit(valid_data_points)

    print "Valid Points {}".format(len(model.core_sample_indices_))
    # print "Valid Points {}".format(valid_data_points)
    print "Number of Labels {}".format(model.labels_.max() + 1)
    # print "Distances: {}".format(pairwise_distances(valid_data_points))

    return label == -1


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
