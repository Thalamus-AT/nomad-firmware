import Tkinter as tk
import tkFont


class gui:
    window = None
    input_values = None
    output_values = None
    io_handler = None

    def __init__(self, io):
        self.io_handler = io

    def run_gui(self):

        self.window = tk.Tk()
        default_font = tkFont.Font(family="Times", size=16)
        self.window.option_add("*Font", default_font)
        self.window.title("Nomad Sensor | Thalamus Assistive Technologies")
        self.window.geometry("500x250")
        self.window.resizable(0, 0)
        self.window.protocol("WM_DELETE_WINDOW", self.window_close_handler)

        left_frame = tk.Frame(master=self.window, width=250, height=250)
        right_frame = tk.Frame(master=self.window, width=250, height=250)

        left_frame.grid_propagate(0)
        right_frame.grid_propagate(0)

        input_label = tk.Label(master=left_frame, text='Sensor Readings:')
        output_label = tk.Label(master=right_frame, text='Output Intensities')

        input_label.place(anchor='center')
        output_label.place(anchor='center')

        input_label.grid(row=0)
        output_label.grid(row=0)

        input_frame = tk.Frame(master=left_frame, width=250, height=200)
        output_frame = tk.Frame(master=right_frame, width=250, height=200)

        input_frame.place(anchor='center')
        output_frame.place(anchor='center')

        input_frame.grid_propagate(0)
        output_frame.grid_propagate(0)

        self.input_values = [None] * 6
        for i in range(len(self.input_values)):
            self.input_values[i] = tk.StringVar()
            tk.Label(master=input_frame, textvariable=self.input_values[i]).grid(row=int(i / 3), column=i % 3)
            self.input_values[i].set('000.000')

        self. output_values = [None] * 3
        for i in range(len(self.output_values)):
            self.output_values[i] = tk.StringVar()
            tk.Label(master=output_frame, textvariable=self.output_values[i]).grid(row=0, column=i)
            self.output_values[i].set('000.000')

        input_frame.grid(row=1)
        output_frame.grid(row=1)

        left_frame.grid(row=0, column=0)
        right_frame.grid(row=0, column=1)

        self.window.mainloop()

    def window_close_handler(self):
        self.io_handler.request_exit()
        self.window.quit()

    def set_values(self, inputs, outputs):
        print('{} | {}'.format(self.input_values, self.output_values))
        assert self.input_values is not None
        assert self.output_values is not None

        for i in range(len(self.input_values)):
            self.input_values[i].set(str(inputs[i])[:7])

        for i in range(len(self.output_values)):
            self.output_values[i].set(str(outputs[i])[:7])
