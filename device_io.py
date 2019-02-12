from pynput import keyboard as kb

requested_exit = False
listener = None


def setup():
    global listener
    listener = kb.Listener(on_release=release_handler)
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
    if key == kb.Key.esc:
        request_exit()


def close():
    global listener
    if listener is not None:
        listener.stop()
