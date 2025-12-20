"""UI Frame definitions for AuraStairs Subscriber."""

import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import matplotlib


class VisualizationFrame(tk.Frame):
    """Frame for displaying motion sensor visualization and graphs."""

    def __init__(self, parent, max_points=50):
        super().__init__(parent)
        self.max_points = max_points
        self.data_queue = deque(maxlen=max_points)

        # Status label
        self.status_label = tk.Label(self, text="Status: DISCONNECTED")
        self.status_label.pack(pady=5)

        # Motion label
        self.motion_label = tk.Label(self, text="Motion: UNKNOWN", font=("Arial", 16))
        self.motion_label.pack(pady=10)

        # Error label
        self.error_label = tk.Label(self, text="Error: NONE")
        self.error_label.pack(pady=5)

        # Indicator canvas
        self.canvas_indicator = tk.Canvas(self, width=60, height=60)
        self.canvas_indicator.pack(pady=10)
        self.indicator = self.canvas_indicator.create_oval(10, 10, 50, 50, fill="gray")

        # Graph setup
        matplotlib.use("TkAgg")
        self.figure = Figure(figsize=(4, 2), dpi=80)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Motion Sensor History")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Motion")
        self.ax.set_ylim(-0.1, 1.1)
        (self.line,) = self.ax.plot([], [], marker="o")

        self.canvas_graph = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_graph.get_tk_widget().pack()

        # Save CSV button
        self.save_csv_btn = tk.Button(
            self, text="Save Last 100 to CSV", command=self.on_save_csv
        )
        self.save_csv_btn.pack(pady=5)

        # Callback for save button
        self._on_save_csv_callback = None

    def set_on_save_csv_callback(self, callback):
        """Set callback for save CSV button."""
        self._on_save_csv_callback = callback

    def on_save_csv(self):
        """Handle save CSV button click."""
        if self._on_save_csv_callback:
            self._on_save_csv_callback()

    def update_motion(self, sensor_value, is_sensor_valid):
        """Update motion display based on sensor value."""
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

    def update_graph(self, sensor_value):
        """Update graph with new sensor value."""
        self.data_queue.append(sensor_value)
        self.line.set_data(range(len(self.data_queue)), list(self.data_queue))
        self.ax.set_xlim(0, self.max_points)
        self.canvas_graph.draw()


class PerformanceTestFrame(tk.Frame):
    """Frame for displaying performance test metrics."""

    def __init__(self, parent):
        super().__init__(parent)

        # Title
        tk.Label(self, text="Performance Test").pack(pady=5)

        # Latency label
        self.latency_label = tk.Label(self, text="Latency: N/A ms")
        self.latency_label.pack()

        # Packet loss label
        self.packet_loss_label = tk.Label(self, text="Packet Loss: N/A")
        self.packet_loss_label.pack()

        # Throughput label
        self.throughput_label = tk.Label(self, text="Throughput: N/A B/s")
        self.throughput_label.pack()

        # Total packets label
        self.total_packets_label = tk.Label(self, text="Received: 0, Expected: 0")
        self.total_packets_label.pack()

        # Download log button
        self.download_log_btn = tk.Button(
            self, text="Download Log", command=self.on_download_log
        )
        self.download_log_btn.pack(pady=5)

        # Callback for download button
        self._on_download_log_callback = None

    def set_on_download_log_callback(self, callback):
        """Set callback for download log button."""
        self._on_download_log_callback = callback

    def on_download_log(self):
        """Handle download log button click."""
        if self._on_download_log_callback:
            self._on_download_log_callback()

    def update_metrics(self, latency_ms, loss_percent, throughput, received, expected):
        """Update performance metrics display."""
        self.latency_label.config(text=f"Latency: {latency_ms:.1f} ms")
        self.packet_loss_label.config(text=f"Packet Loss: {loss_percent:.1f}%")
        self.throughput_label.config(text=f"Throughput: {throughput:.1f} B/s")
        self.total_packets_label.config(
            text=f"Received: {received}, Expected: {expected}"
        )


class ConfigFrame(tk.Frame):
    """Frame for configuration settings."""

    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Update Config GUI Placeholder").pack(pady=50)
