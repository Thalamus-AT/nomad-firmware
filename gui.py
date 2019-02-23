import Tkinter as tk
import tkFont


class gui:
    window = None
    input_values = None
    output_values = None
    normalised_change = None
    io_handler = None

    width = 0
    height = 0

    def __init__(self, io, width=500, height=250):
        self.io_handler = io
        self.width = width
        self.height = height

    def run_gui(self):

        self.window = tk.Tk()
        default_font = tkFont.Font(family='Times', size=16)
        self.window.option_add('*Font', default_font)
        self.window.title('Nomad Sensor | Thalamus Assistive Technologies')
        self.window.geometry('{}x{}'.format(self.width, self.height))
        self.window.resizable(0, 0)
        self.window.protocol('WM_DELETE_WINDOW', self.window_close_handler)

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

        self.input_values = [None] * 6
        for i in range(len(self.input_values)):
            self.input_values[i] = tk.StringVar()
            tk.Label(master=input_frame, textvariable=self.input_values[i]) \
                .grid(row=int(i / 3), column=i % 3, padx=6, pady=2)
            self.input_values[i].set('000.000')

        self. output_values = [None] * 3
        for i in range(len(self.output_values)):
            self.output_values[i] = tk.StringVar()
            tk.Label(master=output_frame, textvariable=self.output_values[i]) \
                .grid(row=0, column=i, padx=6, pady=2)
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

        self.normalised_change = [None] * 6
        for i in range(len(self.normalised_change)):
            self.normalised_change[i] = tk.StringVar()
            tk.Label(master=change_frame, textvariable=self.normalised_change[i]) \
                .grid(row=int(i / 3)+1, column=i % 3, padx=6, pady=2)
            self.normalised_change[i].set('000.000')

        change_frame.grid(column=0)
        bottom_frame.grid(row=1, columnspan=2)

        self.window.mainloop()

    def window_close_handler(self):
        self.io_handler.request_exit()
        self.window.quit()

    def set_values(self, inputs, outputs, change):
        assert self.input_values is not None
        assert self.output_values is not None

        for i in range(len(self.input_values)):
            self.input_values[i].set(str(inputs[i])[:7])

        for i in range(len(self.output_values)):
            self.output_values[i].set(str(outputs[i])[:7])

        for i in range(len(self.normalised_change)):
            self.normalised_change[i].set(str(change[i])[:7])
