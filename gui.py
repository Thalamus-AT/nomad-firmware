import Tkinter as tk
import tkFont
from threading import Thread

gui_process = None
io = None
window = None

input_values = None
output_values = None


def run_gui():
    global window, input_values, output_values

    window = tk.Tk()
    default_font = tkFont.Font(family="Times", size=16)
    window.option_add("*Font", default_font)
    window.title("Nomad Sensor | Thalamus Assistive Technologies")
    window.geometry("500x250")
    window.resizable(0, 0)
    window.protocol("WM_DELETE_WINDOW", window_close_handler)

    left_frame = tk.Frame(master=window, width=250, height=250)
    right_frame = tk.Frame(master=window, width=250, height=250)

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

    input_values = [None] * 6
    for i in range(len(input_values)):
        input_values[i] = tk.StringVar()
        tk.Label(master=input_frame, textvariable=input_values[i]).grid(row=int(i / 3), column=i % 3)
        input_values[i].set('000.000')

    output_values = [None] * 3
    for i in range(len(output_values)):
        output_values[i] = tk.StringVar()
        tk.Label(master=output_frame, textvariable=output_values[i]).grid(row=0, column=i)
        output_values[i].set('000.000')

    input_frame.grid(row=1)
    output_frame.grid(row=1)

    left_frame.grid(row=0, column=0)
    right_frame.grid(row=0, column=1)

    window.mainloop()


def window_close_handler():
    io.request_exit()
    window.destroy()


def start_gui(io_handler):
    global gui_process, io

    io = io_handler

    gui_process = Thread(target=run_gui)
    gui_process.start()


def set_values(inputs, outputs):
    global input_values, output_values

    assert input_values is not None
    assert output_values is not None

    for i in range(len(input_values)):
        input_values[i].set(str(inputs[i])[:7])

    for i in range(len(output_values)):
        output_values[i].set(str(outputs[i])[:7])


def close():
    window.quit()
    gui_process.join()
