from pynput.keyboard import Key, Listener

requested_exit = False
listener = None


def setup():
    global listener
    listener = Listener(on_release=release_handler)
    listener.start()


# Called when the user wants to exit
def request_exit():
    global requested_exit
    requested_exit = True


# Called by the main loop to check whether to exit
def has_requested_exit():
    return requested_exit


def release_handler(key):
    print('Key Pressed ({})'.format(key))
    if key == Key.esc:
        request_exit()


def close():
    global listener
    if listener is not None:
        listener.stop()
