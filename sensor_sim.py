# Test functions used to test the processing without direct sensor input.
# Reads in test data from a CSV file

import time

TEST_FILE = "data/nomad-reading-4.data"

count = 0
max_line = 0


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
