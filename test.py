import csv
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk
from ttkbootstrap import Style
import matplotlib.pyplot as plt

root = tk.Tk()
root.title("Log Analyzer")
style = Style(theme='darkly')

lists_dict = {}
checked_vars = {}

with open('LOG.csv', newline='') as f:
    reader = csv.reader(f)
    first_row = next(reader)

    for item in first_row:
        lists_dict[item] = []

    for row in reader:
        for i in range(len(first_row)):
            lists_dict[first_row[i]].append(row[i])


variables = {var_name: tk.BooleanVar() for var_name in first_row[1:]}
# print(variables)

fig = Figure(figsize=(8, 6), dpi=100)
# plots = {}


# Plot Function
def create_plot():
    global plots_frame
    global checked_vars
    global canvas_fig
    # checked_vars = {}
    #
    # for ax in plots.values():
    #     ax.clear()

    checked_vars = [var_name for var_name, var in variables.items() if var.get()]
    num_plots = len(checked_vars)

    # Clear Previous Plots

    for widget in plots_frame.winfo_children():
        widget.destroy()

    # Create Plots

    # num_plots = len(checked_vars)
    # rows = num_plots // 2 + num_plots % 2  # Calculate number of rows
    # cols = 2  # Set number of columns

    for z, items in enumerate(checked_vars, start=1):
        print(lists_dict[items])

        # plotting the graph
        ax = fig.add_subplot(len(checked_vars), 1, z)
        ax.plot(lists_dict['vtime'], lists_dict[items], label=items)
        # Adjust layout
        ax.set_title(items)
        ax.set_xlabel('Time')
        ax.set_ylabel(f'{items}')
        ax.legend()
        # plot1.grid(True)
        # fig.tight_layout()

        # plots[items] = ax
        # Draw canvas
        canvas_fig.draw()


# Create Frame
main_frame = tk.Frame(root, bg='white')
main_frame.pack(fill=tk.BOTH, expand=1, padx=20, pady=20)


# Create Frame Inside Canvas
checkbox_frame = tk.Frame(main_frame)
checkbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Create Frame Inside Canvas
plots_frame = tk.Frame(main_frame)
plots_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# # Create Canvas
# canvas = tk.Canvas(main_frame)
# canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# # Create Scrollbar
# scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# # Configure Canvas
# canvas.configure(yscrollcommand=scrollbar.set)
# canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
#
# canvas.create_window((0, 0), window=checkbox_frame, anchor=tk.NW)
# canvas.create_window((0, 0), window=plots_frame, anchor=tk.SW)

# Add Checkboxes
i = j = 0
checkboxes = []

for item1, item2 in zip(first_row[1:], variables.values()):
    checkbox_var = tk.BooleanVar(value=False)
    test = ttk.Checkbutton(checkbox_frame, text=f"{item1}", variable=item2, style='TCheckbutton')
    # test.grid(row=i, column=j, sticky="w")
    test.grid(row=i, column=0, sticky="w", padx=5, pady=5)
    checkboxes.append(test)
    # test.grid(row=i // 5, column=i % 5, pax=5, pay=5, sticky='w')
    # j += 1
    # if j == 5:
    #     i += 1
    #     j = 0


# Add Plot Button

button = ttk.Button(root, text='plot', command=create_plot, style='TButton')
# button.pack(pady=10)
button.grid(row=len(first_row[1:]), column=0, pady=10)


# Embed the Matplotlib plot in the Tkinter GUI using FigureCanvasTkAgg
canvas_fig = FigureCanvasTkAgg(fig, master=plots_frame)
# canvas_fig.draw()
# canvas_fig.get_tk_widget().grid(row=i+2, column=6)
# canvas_fig.get_tk_widget().grid(row=len(variables) + 1, column=0, pady=10)
# canvas_widget = canvas_fig.get_tk_widget()
# canvas_widget.pack(fill=tk.BOTH, expand=True)
canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()
