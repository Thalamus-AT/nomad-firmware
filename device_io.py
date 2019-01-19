
requested_exit = False


# Called when the user wants to exit
def request_exit():
    global requested_exit
    requested_exit = True


# Called by the main loop to check whether to exit
def has_requested_exit():
    return requested_exit
