import array

intensities = array.array('I', [0, 0])


def set_pad_intensity(pad, intensity):
    intensities[pad] = intensity


def get_pad_intensity(pad):
    return intensities[pad]

