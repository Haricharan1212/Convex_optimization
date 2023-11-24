from plotting import plot_loss
import tkinter as tk
from tkinter import ttk

def get_values():
    
    global a, b, c, d, e
    a = variable_a.get()
    b = variable_b.get()
    c = entry_c.get()
    d = entry_d.get()
    e = entry_e.get()

    print("Running Code")
    plot_loss(str(a), float(c), int(100/int(b)), int(d), int(e))

# Create the main window
root = tk.Tk()
root.title("Convex Optimization")

# Create and place drop-down menus
label_a = tk.Label(root, text="Select dataset:")
label_a.grid(row=0, column=0, padx=10, pady=10)
options_a = ["news20.binary", "phishing", "heart_scale"]
variable_a = tk.StringVar(root)
variable_a.set(options_a[0])
dropdown_a = ttk.Combobox(root, textvariable=variable_a, values=options_a)
dropdown_a.grid(row=0, column=1, padx=10, pady=10)

label_b = tk.Label(root, text="Select percentage of data used:")
label_b.grid(row=1, column=0, padx=10, pady=10)
options_b = [1, 5, 10, 20]
variable_b = tk.StringVar(root)
variable_b.set(options_b[2])
dropdown_b = ttk.Combobox(root, textvariable=variable_b, values=options_b)
dropdown_b.grid(row=1, column=1, padx=10, pady=10)

# Create and place input boxes
label_c = tk.Label(root, text="Enter tolerance:")
label_c.grid(row=2, column=0, padx=10, pady=10)
entry_c = tk.Entry(root, textvariable=tk.StringVar(value=1e-5))
entry_c.grid(row=2, column=1, padx=10, pady=10)

label_d = tk.Label(root, text="Enter outer loop iterations:")
label_d.grid(row=3, column=0, padx=10, pady=10)
entry_d = tk.Entry(root, textvariable=tk.StringVar(value=100))
entry_d.grid(row=3, column=1, padx=10, pady=10)

label_e = tk.Label(root, text="Enter max_CG")
label_e.grid(row=4, column=0, padx=10, pady=10)
entry_e = tk.Entry(root, textvariable=tk.StringVar(value=5))
entry_e.grid(row=4, column=1, padx=10, pady=10)

# Create a button to get values
button_get_values = tk.Button(root, text="Run Command", command=get_values)
button_get_values.grid(row=5, column=0, columnspan=2, pady=10)

# Run the Tkinter event loop
root.mainloop()
