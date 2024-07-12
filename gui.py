import tkinter as tk

root = tk.Tk()
root.title("Log Analyzer")

var1 = tk.BooleanVar()
var2 = tk.BooleanVar()


def show_state():
    print("Checkboxes state:")
    print("Checkbox 1:", var1.get())
    print("Checkbox 2:", var2.get())

ch = []
checkbox1 = tk.Checkbutton(root, text="Checkbox 1", variable=var1)
ch.appk.Checkbutton(root, text="Checkbox 2", variable=var2)

# Position checkboxes using grid layout manager
checkbox1.grid(row=0, column=0, sticky="w")
# checkbox2.grid(row=1, column=0, sticky="w")

# Button to display the state of checkboxes
show_button = tk.Button(root, text="plot", command=show_state)
show_button.grid(row=2, column=0, pady=10)

root.mainloop()
