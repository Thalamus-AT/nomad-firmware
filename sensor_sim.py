import time

# ==============================================================
# This file is exclusively used to simulate the sensor_driver
# file when it is actually connected to the sensors. This is
# done so the program can be tested on a device which isn't the
# Raspberry Pi.
# ==============================================================

TEST_FILE = "data/nomad-reading-4.data"     # The name of the file we will be reading from.

count = 0       # The current line of the file we are reading from.
max_line = 0    # The number of lines in the file.


# Returns the length of a file
def file_len(fname):
    f = open(fname, 'r')

    i = 0
    for i, l in enumerate(f):
        pass

    f.close()

    return i + 1


# Initialises the test data
def setup_sensors(p):
    global count, max_line

    count = 0
    max_line = file_len(TEST_FILE)
    print("Initialising Sensors")
    print("File ({}) contains {} lines".format(TEST_FILE, max_line))
    print

    time.sleep(1)


# Reads the next line of data from the file and returns it as a 1x9 array of ints
# If it has reached the end of the file it will loop around to the start again
def poll_sensors():
    global count

    with open(TEST_FILE, 'r') as f:
        for i, line in enumerate(f):
            if i == count:
                count = (count + 1) % max_line
                return map(float, map(str.strip, line.split(',')))[:6]


def close():
    return
