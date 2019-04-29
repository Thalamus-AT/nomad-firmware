import Tkinter as tk
import tkFont

# Duplicates of configuration values in processing.py
NUM_OF_SENSORS = 6
NUM_OF_OUTPUTS = 3
MAX_SENSOR_VAL = 250.


# The GUI class used to run and update the GUI.
class gui:
    window = None
    io_handler = None

    # Arrays to store the displayed values.
    input_values = [None] * NUM_OF_SENSORS
    input_labels = [None] * NUM_OF_SENSORS
    output_values = [None] * NUM_OF_OUTPUTS
    output_labels = [None] * NUM_OF_OUTPUTS
    change_values = [None] * NUM_OF_SENSORS
    change_labels = [None] * NUM_OF_SENSORS

    width = 0
    height = 0

    # Constructor for the GUI.
    def __init__(self, io, width=500, height=250):
        self.io_handler = io
        self.width = width
        self.height = height

    # Sets up the structure of the GUI and runs the main loop to render it.
    def run_gui(self):
        self.window = tk.Tk()
        default_font = tkFont.Font(family='Times', size=16)
        self.window.option_add('*Font', default_font)
        self.window.title('Nomad Sensor | Thalamus Assistive Technologies')
        self.window.geometry('{}x{}'.format(self.width, self.height))
        self.window.resizable(0, 0)

        # Add a handler for closing the window.
        self.window.protocol('WM_DELETE_WINDOW', self.window_close_handler)

        # Define the different sections of the GUI, and the elements that exist within them.
        left_frame = tk.Frame(master=self.window, width=self.width/2, height=self.height/2)
        right_frame = tk.Frame(master=self.window, width=self.width/2, height=self.height/2)

        left_frame.grid_propagate(0)
        right_frame.grid_propagate(0)

        input_label = tk.Label(master=left_frame, text='Sensor Readings:')
        output_label = tk.Label(master=right_frame, text='Output Intensities')

        input_label.place(anchor='center')
        output_label.place(anchor='center')

        input_label.grid(row=0)
        output_label.grid(row=0)

        input_frame = tk.Frame(master=left_frame, width=self.width/2, height=self.height/2 - 20)
        output_frame = tk.Frame(master=right_frame, width=self.width/2, height=self.height/2 - 20)

        input_frame.place(anchor='center')
        output_frame.place(anchor='center')

        input_frame.grid_propagate(0)
        output_frame.grid_propagate(0)

        # Add the labels for displaying the sensor readings.
        for i in range(NUM_OF_SENSORS):
            self.input_values[i] = tk.StringVar()
            self.input_labels[i] = tk.Label(master=input_frame, textvariable=self.input_values[i])
            self.input_labels[i].grid(row=int(i / 3), column=i % 3, padx=6, pady=2)
            self.input_values[i].set('000.000')

        # Add the labels for displaying the vibration intensities.
        for i in range(NUM_OF_OUTPUTS):
            self.output_values[i] = tk.StringVar()
            self.output_labels[i] = tk.Label(master=output_frame, textvariable=self.output_values[i])
            self.output_labels[i].grid(row=0, column=i, padx=6, pady=2)
            self.output_values[i].set('000.000')

        input_frame.grid(row=1)
        output_frame.grid(row=1)

        left_frame.grid(row=0, column=0)
        right_frame.grid(row=0, column=1)

        bottom_frame = tk.Frame(master=self.window, width=self.width, height=self.height/2)
        bottom_frame.grid_propagate(0)

        change_label = tk.Label(master=bottom_frame, text='Normalised Change: ')
        change_label.place(anchor='center')
        change_label.grid(row=0)

        change_frame = tk.Frame(master=bottom_frame, width=self.width/2, height=self.height/2 - 20)
        change_frame.place(anchor='center')
        change_frame.grid_propagate(0)

        # Add the labels for displaying the normalised change values.
        for i in range(NUM_OF_SENSORS):
            self.change_values[i] = tk.StringVar()
            self.change_labels[i] = tk.Label(master=change_frame, textvariable=self.change_values[i])
            self.change_labels[i].grid(row=int(i / 3)+1, column=i % 3, padx=6, pady=2)
            self.change_values[i].set('0.00000')

        change_frame.grid(column=0)
        bottom_frame.grid(row=1, columnspan=2)

        # Begin the main loop that renders the window.
        self.window.mainloop()

    # Handles when the user clicks the x in the top right of the window, to close it.
    def window_close_handler(self):
        # Inform the program that the user has requested exit.
        self.io_handler.request_exit()

        # Close the window.
        self.window.quit()

    # Updates the values displayed on the GUI.
    def set_values(self, inputs, outputs, change):

        # Check that the values to be displayed have all been initialised.
        assert None not in self.input_values
        assert None not in self.input_labels
        assert None not in self.output_values
        assert None not in self.output_labels
        assert None not in self.change_values
        assert None not in self.change_labels

        # Update the sensor readings.
        for i in range(NUM_OF_SENSORS):
            self.input_values[i].set(self.format_num_string(inputs[i], 3, 3))

            rgb_code = self.from_rgb((220, 220 - (((MAX_SENSOR_VAL - inputs[i]) / MAX_SENSOR_VAL) * 220), 220))
            self.input_labels[i].config(bg=rgb_code)

        # Update the vibration intensities.
        for i in range(NUM_OF_OUTPUTS):
            self.output_values[i].set(self.format_num_string(outputs[i], 3, 3))

            rgb_code = self.from_rgb((220, 220 - ((outputs[i] / 100.) * 220), 220))
            self.output_labels[i].config(bg=rgb_code)

        # Updae the normalised change values.
        for i in range(NUM_OF_SENSORS):
            self.change_values[i].set(self.format_num_string(change[i], 1, 5))

            rgb_code = self.from_rgb((220, 220 - (change[i] * 220), 220))
            self.change_labels[i].config(bg=rgb_code)

    # Converts red, green, and blue values to hex code for the colour.
    @staticmethod
    def from_rgb(rgb):
        return "#%02x%02x%02x" % rgb

    # Formats a number into a specific format, with a number of digits before and after the decimal point.
    @staticmethod
    def format_num_string(num, min_left, right):
        # Get a string from the number and split it into the pre-decimal and post-decimal parts.
        num_string = str(num)
        parts = num_string.split('.')

        if len(parts) < 2:
            parts.append('')

        # Append parts to the left side until it is of min length.
        if len(parts[0]) < min_left:
            parts[0] = ('0' * (min_left - len(parts[0]))) + parts[0]

        # Truncate or append values until the right side is the correct length.
        if len(parts[1]) > right:
            parts[1] = parts[1][:right]
        elif len(parts[1]) < right:
            parts[1] = parts[1] + ('0' * (right - len(parts[1])))

        # Assert that the lengths are correct.
        assert len(parts[0]) >= min_left
        assert len(parts[1]) == right

        # Return the parts appended together.
        return parts[0] + '.' + parts[1]
