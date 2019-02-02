import array

intensities = array.array('I', [0, 0, 0])


def set_pad_intensity(pad, intensity):
    intensities[pad] = intensity


def set_all_intensities(values):
    intensities[0] = int(values[0])
    intensities[1] = int(values[1])
    intensities[2] = int(values[2])


def get_pad_intensity(pad):
    return intensities[pad]

