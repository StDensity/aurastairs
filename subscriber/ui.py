import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")  # use TkAgg backend for Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque


class SubscriberUI:
    def __init__(self, root, max_points=50):
        self.root = root
        self.root.title("AuraStairs – Motion Monitor")
        self.root.geometry("400x400")
        self.root.resizable(False, False)

        self.status_label = tk.Label(root, text="Status: DISCONNECTED")
        self.status_label.pack(pady=5)

        self.motion_label = tk.Label(root, text="Motion: UNKNOWN", font=("Arial", 16))
        self.motion_label.pack(pady=10)

        self.error_label = tk.Label(root, text="Error: NONE")
        self.error_label.pack(pady=5)

        self.canvas_indicator = tk.Canvas(root, width=60, height=60)
        self.canvas_indicator.pack(pady=10)
        self.indicator = self.canvas_indicator.create_oval(10, 10, 50, 50, fill="gray")

        # Button frame
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.visualize_btn = tk.Button(self.button_frame, text="Visualization", command=self._visualization)
        self.visualize_btn.grid(row=0, column=0, padx=5)

        self.perf_test_btn = tk.Button(self.button_frame, text="Performance Test", command=self._performance_test)
        self.perf_test_btn.grid(row=0, column=1, padx=5)

        self.update_cfg_btn = tk.Button(self.button_frame, text="Update Config", command=self._update_config)
        self.update_cfg_btn.grid(row=0, column=2, padx=5)

        # Graph setup
        self.max_points = max_points
        self.data_queue = deque(maxlen=max_points)
        self.figure = Figure(figsize=(4, 2), dpi=80)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Motion Sensor History")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Motion")
        self.ax.set_ylim(-0.1, 1.1)
        self.line, = self.ax.plot([], [], marker='o')

        self.canvas_graph = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_graph.get_tk_widget().pack()

    # Update UI from MQTT data
    def update_from_data(self, data):
        self.root.after(0, self._update_ui, data)

    def _update_ui(self, data):
        sensor_value = data.get("sensor_value", 0)
        is_sensor_valid = data.get("is_sensor_valid", False)

        self.status_label.config(text="Status: CONNECTED")

        if sensor_value:
            self.motion_label.config(text="Motion: YES")
            self.canvas_indicator.itemconfig(self.indicator, fill="green")
        else:
            self.motion_label.config(text="Motion: NO")
            self.canvas_indicator.itemconfig(self.indicator, fill="red")

        self.error_label.config(text=f"Error: {is_sensor_valid}")

        # Update graph
        self.data_queue.append(sensor_value)
        self.line.set_data(range(len(self.data_queue)), list(self.data_queue))
        self.ax.set_xlim(0, self.max_points)
        self.canvas_graph.draw()

    # Dummy button callbacks
    def _visualization(self):
        messagebox.showinfo("Visualization", "Visualization already active.")

    def _performance_test(self):
        messagebox.showinfo("Performance Test", "Dummy Performance Test executed.")

    def _update_config(self):
        messagebox.showinfo("Update Config", "Dummy Update Config executed.")
