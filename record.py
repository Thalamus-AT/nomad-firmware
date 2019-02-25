import time

import sensor_driver as sd

POLL_TIME = 0.2


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
            f.write(','.join([str(i) for i in inputs]) + '\n')

        # Wait until the next step is reached.
        while time.time() < last_time + POLL_TIME:
            time.sleep(0.01)

    sd.close()


if __name__ == '__main__':
    main()
