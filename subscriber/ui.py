"""Main UI orchestrator for AuraStairs Subscriber."""

import tkinter as tk
from collections import deque
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ui_frames import VisualizationFrame, PerformanceTestFrame, ConfigFrame
from ui_utils import save_sensor_csv, save_perf_log, calculate_perf_metrics

config.load()


class SubscriberUI:
    """Main UI class for AuraStairs Subscriber."""

    def __init__(self, root, max_points=50, publish_config_callback=None):
        self.root = root
        self.root.title("AuraStairs – Motion Monitor")
        self.root.geometry("500x500")
        self.root.resizable(False, False)

        # Store publish callback
        self.publish_config_callback = publish_config_callback

        # UI state
        self.mode = "visualization"
        self.current_frame = None

        # Performance test state
        self.first_seq = None
        self.last_seq = None
        self.total_received = 0
        self.total_expected = 0
        self.missed_packets = 0
        self.total_bytes = 0

        # Sensor logging
        self.max_sensor_log = config.get("max_sensor_log", 150)
        self.sensor_log = deque(maxlen=self.max_sensor_log)

        # Setup scrollable container
        self._setup_scrollable_container()

        # Setup navigation buttons
        self._setup_button_frame()

        # Setup frame instances
        self.visualization_frame = VisualizationFrame(self.content_frame, max_points)
        self.visualization_frame.set_on_save_csv_callback(self._on_save_csv)

        self.perf_test_frame = PerformanceTestFrame(self.content_frame)
        self.perf_test_frame.set_on_download_log_callback(self._on_download_perf_log)

        # Setup config frame (don't pack it yet)
        self.config_frame = ConfigFrame(
            self.content_frame, publish_callback=self.publish_config_callback
        )
        self.config_frame.set_config_values(config._config)
        self.config_frame.update_config_btn.config(
            command=self.config_frame.on_update_config
        )

        # Show default frame
        self.show_visualization()

    def _setup_scrollable_container(self):
        """Setup the scrollable canvas and content frame."""
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.vscrollbar = tk.Scrollbar(self.top_frame, orient=tk.VERTICAL)
        self.vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.hscrollbar = tk.Scrollbar(self.top_frame, orient=tk.HORIZONTAL)
        self.hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(
            self.top_frame,
            yscrollcommand=self.vscrollbar.set,
            xscrollcommand=self.hscrollbar.set,
            highlightthickness=0,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vscrollbar.config(command=self.canvas.yview)
        self.hscrollbar.config(command=self.canvas.xview)

        self.content_frame = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.content_frame, anchor="nw")

        # Configure scroll region
        def on_frame_configure(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        self.content_frame.bind("<Configure>", on_frame_configure)

        # Bind mousewheel scrolling
        self.canvas.bind(
            "<MouseWheel>",
            lambda e: self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units"),
        )
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _setup_button_frame(self):
        """Setup navigation buttons."""
        self.button_frame = tk.Frame(self.content_frame)
        self.button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.visualize_btn = tk.Button(
            self.button_frame, text="Visualization", command=self.show_visualization
        )
        self.visualize_btn.pack(side=tk.LEFT, padx=5)

        self.perf_test_btn = tk.Button(
            self.button_frame, text="Performance Test", command=self.show_perf_test
        )
        self.perf_test_btn.pack(side=tk.LEFT, padx=5)

        self.update_cfg_btn = tk.Button(
            self.button_frame, text="Update Config", command=self.show_update_config
        )
        self.update_cfg_btn.pack(side=tk.LEFT, padx=5)

    def _switch_frame(self, new_frame):
        """Switch to a different frame."""
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = new_frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_visualization(self):
        """Show visualization frame."""
        self.mode = "visualization"
        self._switch_frame(self.visualization_frame)

    def show_perf_test(self):
        """Show performance test frame."""
        self.mode = "performance"
        self._switch_frame(self.perf_test_frame)

    def show_update_config(self):
        """Show config frame."""
        self.mode = "config"
        self._switch_frame(self.config_frame)

    def update_from_data(self, data):
        """Update UI with incoming sensor data."""
        if self.mode == "visualization":
            self.root.after(0, self._update_visualization, data)
        elif self.mode == "performance":
            self.root.after(0, self._update_performance, data)

    def _update_visualization(self, data):
        """Update visualization frame with sensor data."""
        sensor_value = data.get("sensor_value", 0)
        is_sensor_valid = data.get("is_sensor_valid", False)

        self.visualization_frame.update_motion(sensor_value, is_sensor_valid)
        self.visualization_frame.update_graph(sensor_value)

        self.sensor_log.append(
            {
                "timestamp": data.get("timestamp"),
                "sensor_value": data.get("sensor_value"),
                "is_sensor_valid": data.get("is_sensor_valid"),
                "seq": data.get("seq"),
            }
        )

    def update_perf_data(self, data):
        """Update performance metrics with incoming data."""
        self.root.after(0, self._update_performance, data)

    def _update_performance(self, data):
        """Update performance frame with data."""
        recv_time = time.time()
        sent_time = data.get("timestamp", recv_time)
        seq = data.get("seq", 0)
        payload_size = len(str(data).encode("utf-8"))

        # Track first sequence
        if self.first_seq is None:
            self.first_seq = seq

        # Update sequence tracking
        self.last_seq = seq
        self.total_received += 1
        self.total_expected = self.last_seq - self.first_seq + 1
        self.missed_packets = self.total_expected - self.total_received

        # Calculate metrics
        latency_ms = (recv_time - sent_time) * 1000
        loss_percent, throughput = calculate_perf_metrics(
            self.missed_packets, self.total_expected, self.total_bytes
        )
        self.total_bytes += payload_size

        # Update UI
        self.perf_test_frame.update_metrics(
            latency_ms,
            loss_percent,
            throughput,
            self.total_received,
            self.total_expected,
        )

    def _on_save_csv(self):
        """Handle save CSV action."""
        filename = f"sensor_log_{int(time.time())}.csv"
        save_sensor_csv(filename, self.sensor_log, folder="logs")

    def _on_download_perf_log(self):
        """Handle download performance log action."""
        filename = "performance_log.txt"
        save_perf_log(
            filename,
            self.total_received,
            self.total_expected,
            self.missed_packets,
            self.total_bytes,
            folder="logs",
        )
