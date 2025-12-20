import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import time

class SubscriberUI:
    def __init__(self, root, max_points=50):
        self.root = root
        self.root.title("AuraStairs – Motion Monitor")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.mode = "visualization"

        # --- Container for dynamic content ---
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # --- Bottom buttons ---
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=5)

        self.visualize_btn = tk.Button(self.button_frame, text="Visualization", command=self.show_visualization)
        self.visualize_btn.grid(row=0, column=0, padx=5)

        self.perf_test_btn = tk.Button(self.button_frame, text="Performance Test", command=self.show_perf_test)
        self.perf_test_btn.grid(row=0, column=1, padx=5)

        self.update_cfg_btn = tk.Button(self.button_frame, text="Update Config", command=self.show_update_config)
        self.update_cfg_btn.grid(row=0, column=2, padx=5)

        # --- Visualization Frame (default) ---
        self.max_points = max_points
        self.data_queue = deque(maxlen=max_points)
        self.visualization_frame = tk.Frame(self.content_frame)

        self.status_label = tk.Label(self.visualization_frame, text="Status: DISCONNECTED")
        self.status_label.pack(pady=5)

        self.motion_label = tk.Label(self.visualization_frame, text="Motion: UNKNOWN", font=("Arial", 16))
        self.motion_label.pack(pady=10)

        self.error_label = tk.Label(self.visualization_frame, text="Error: NONE")
        self.error_label.pack(pady=5)

        self.canvas_indicator = tk.Canvas(self.visualization_frame, width=60, height=60)
        self.canvas_indicator.pack(pady=10)
        self.indicator = self.canvas_indicator.create_oval(10, 10, 50, 50, fill="gray")

        # Graph
        import matplotlib
        matplotlib.use("TkAgg")
        self.figure = Figure(figsize=(4, 2), dpi=80)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Motion Sensor History")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Motion")
        self.ax.set_ylim(-0.1, 1.1)
        self.line, = self.ax.plot([], [], marker='o')

        self.canvas_graph = FigureCanvasTkAgg(self.figure, master=self.visualization_frame)
        self.canvas_graph.get_tk_widget().pack()

        # --- Placeholder frames ---
        self.perf_test_frame = tk.Frame(self.content_frame)
        tk.Label(self.perf_test_frame, text="Performance Test GUI Placeholder").pack(pady=50)

        self.update_config_frame = tk.Frame(self.content_frame)
        tk.Label(self.update_config_frame, text="Update Config GUI Placeholder").pack(pady=50)

        # Show default frame
        self.current_frame = None
        self.show_visualization()

         # --- Performance test frame ---
        self.perf_test_frame = tk.Frame(self.content_frame)

        tk.Label(self.perf_test_frame, text="Performance Test").pack(pady=5)

        self.latency_label = tk.Label(self.perf_test_frame, text="Latency: N/A ms")
        self.latency_label.pack()

        self.packet_loss_label = tk.Label(self.perf_test_frame, text="Packet Loss: N/A")
        self.packet_loss_label.pack()

        self.throughput_label = tk.Label(self.perf_test_frame, text="Throughput: N/A B/s")
        self.throughput_label.pack()

        # Keep track
        self.last_seq = None
        self.total_packets = 0
        self.missed_packets = 0
        self.total_bytes = 0

    # --- Switching frames ---
    def _switch_frame(self, new_frame):
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = new_frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_visualization(self):
        self.mode = "visualization"
        self._switch_frame(self.visualization_frame)

    def show_perf_test(self):
        self.mode = "performance"
        self._switch_frame(self.perf_test_frame)

    def show_update_config(self):
        self.mode = "config"
        self._switch_frame(self.update_config_frame)

    # --- Update visualization data ---
    def update_from_data(self, data):
        if self.mode == "visualization":
            self.root.after(0, self._update_ui, data)
        elif self.mode == "performance":
            self.root.after(0, self._update_perf_ui, data)

    def _update_ui(self, data):
        sensor_value = data.get("sensor_value", 0)
        is_sensor_valid = data.get("is_sensor_valid", False)

        self.status_label.config(text="Status: CONNECTED")

        if sensor_value == 1:
            self.motion_label.config(text="Motion: YES")
            self.canvas_indicator.itemconfig(self.indicator, fill="green")
        elif sensor_value == 0:
            self.motion_label.config(text="Motion: NO")
            self.canvas_indicator.itemconfig(self.indicator, fill="red")
        else:
            self.motion_label.config(text="Motion: UNKNOWN")
            self.canvas_indicator.itemconfig(self.indicator, fill="gray")

        self.error_label.config(text=f"Error: {not is_sensor_valid}")

        # Update graph
        self.data_queue.append(sensor_value)
        self.line.set_data(range(len(self.data_queue)), list(self.data_queue))
        self.ax.set_xlim(0, self.max_points)
        self.canvas_graph.draw()

    def update_perf_data(self, data):
        self.root.after(0, self._update_perf_ui, data)

    def _update_perf_ui(self, data):
        recv_time = time.time()
        sent_time = data.get("timestamp", recv_time)
        seq = data.get("seq", 0)
        payload_size = len(str(data).encode("utf-8"))

        # --- Latency ---
        latency_ms = (recv_time - sent_time) * 1000
        self.latency_label.config(text=f"Latency: {latency_ms:.1f} ms")

        # --- Packet loss ---
        self.total_packets += 1
        if self.last_seq is not None:
            missed = max(0, seq - self.last_seq - 1)
            self.missed_packets += missed
        self.last_seq = seq
        loss_percent = (self.missed_packets / self.total_packets) * 100
        self.packet_loss_label.config(text=f"Packet Loss: {loss_percent:.1f}%")

        # --- Throughput (approx) ---
        self.total_bytes += payload_size
        elapsed_sec = max(1, self.total_packets * 3)  # assuming publisher interval ~3s
        throughput = self.total_bytes / elapsed_sec
        self.throughput_label.config(text=f"Throughput: {throughput:.1f} B/s")