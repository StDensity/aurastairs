import tkinter as tk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import time, matplotlib, os, sys, csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

config.load()


class SubscriberUI:
    def __init__(self, root, max_points=50):
        self.root = root
        self.root.title("AuraStairs – Motion Monitor")
        self.root.geometry("500x500")
        self.root.resizable(False, False)
        self.mode = "visualization"
        self.first_seq = None
        self.last_seq = None
        self.total_received = 0
        self.total_expected = 0
        self.missed_packets = 0
        self.max_sensor_log = config.get("max_sensor_log", 150)
        self.sensor_log = deque(maxlen=self.max_sensor_log)
        # --- Top container for scrollable content ---
        self.top_frame = tk.Frame(root)
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
        self.canvas.bind(
            "<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units")
        )  # Linux scroll up
        self.canvas.bind(
            "<Button-5>", lambda e: self.canvas.yview_scroll(1, "units")
        )  # Linux scroll down

        # --- Top buttons inside scrollable content ---
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

        # --- Visualization Frame (default) ---
        self.max_points = max_points
        self.data_queue = deque(maxlen=max_points)
        self.visualization_frame = tk.Frame(self.content_frame)

        self.status_label = tk.Label(
            self.visualization_frame, text="Status: DISCONNECTED"
        )
        self.status_label.pack(pady=5)

        self.motion_label = tk.Label(
            self.visualization_frame, text="Motion: UNKNOWN", font=("Arial", 16)
        )
        self.motion_label.pack(pady=10)

        self.error_label = tk.Label(self.visualization_frame, text="Error: NONE")
        self.error_label.pack(pady=5)

        self.canvas_indicator = tk.Canvas(self.visualization_frame, width=60, height=60)
        self.canvas_indicator.pack(pady=10)
        self.indicator = self.canvas_indicator.create_oval(10, 10, 50, 50, fill="gray")

        # Graph

        matplotlib.use("TkAgg")
        self.figure = Figure(figsize=(4, 2), dpi=80)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Motion Sensor History")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Motion")
        self.ax.set_ylim(-0.1, 1.1)
        (self.line,) = self.ax.plot([], [], marker="o")

        self.canvas_graph = FigureCanvasTkAgg(
            self.figure, master=self.visualization_frame
        )
        self.canvas_graph.get_tk_widget().pack()

        # --- Save CSV button in visualization frame ---
        self.save_csv_btn = tk.Button(
            self.visualization_frame,
            text="Save Last 100 to CSV",
            command=self.save_sensor_csv,
        )
        self.save_csv_btn.pack(pady=5)

        # --- Placeholder frames ---
        self.perf_test_frame = tk.Frame(self.content_frame)
        tk.Label(self.perf_test_frame, text="Performance Test GUI Placeholder").pack(
            pady=50
        )

        self.update_config_frame = tk.Frame(self.content_frame)
        tk.Label(self.update_config_frame, text="Update Config GUI Placeholder").pack(
            pady=50
        )

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

        self.throughput_label = tk.Label(
            self.perf_test_frame, text="Throughput: N/A B/s"
        )
        self.throughput_label.pack()

        self.total_packets_label = tk.Label(
            self.perf_test_frame, text="Received: 0, Expected: 0"
        )
        self.total_packets_label.pack()

        self.download_log_btn = tk.Button(
            self.perf_test_frame, text="Download Log", command=self.download_perf_log
        )
        self.download_log_btn.pack(pady=5)

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

        self.sensor_log.append(
            {
                "timestamp": data.get("timestamp"),
                "sensor_value": data.get("sensor_value"),
                "is_sensor_valid": data.get("is_sensor_valid"),
                "seq": data.get("seq"),
            }
        )

    def update_perf_data(self, data):
        self.root.after(0, self._update_perf_ui, data)

    def _update_perf_ui(self, data):
        recv_time = time.time()
        sent_time = data.get("timestamp", recv_time)
        seq = data.get("seq", 0)
        payload_size = len(str(data).encode("utf-8"))

        # --- First sequence ---
        if self.first_seq is None:
            self.first_seq = seq

        # --- Update last sequence ---
        self.last_seq = seq

        # --- Total packets ---
        self.total_received += 1
        self.total_expected = self.last_seq - self.first_seq + 1
        self.missed_packets = self.total_expected - self.total_received

        # --- Latency ---
        latency_ms = (recv_time - sent_time) * 1000
        self.latency_label.config(text=f"Latency: {latency_ms:.1f} ms")

        # --- Packet loss ---
        loss_percent = (self.missed_packets / self.total_expected) * 100
        self.packet_loss_label.config(text=f"Packet Loss: {loss_percent:.1f}%")

        # --- Throughput (approx) ---
        self.total_bytes += payload_size
        elapsed_sec = max(1, self.total_expected * 3)  # 3s publisher interval assumed
        throughput = self.total_bytes / elapsed_sec
        self.throughput_label.config(text=f"Throughput: {throughput:.1f} B/s")

        # --- Total received vs expected ---
        self.total_packets_label.config(
            text=f"Received: {self.total_received}, Expected: {self.total_expected}"
        )

    def download_perf_log(self):
        filename = "performance_log.txt"
        try:
            with open(filename, "w") as f:
                f.write(f"Performance Test Log\n")
                f.write(f"Total Received Packets: {self.total_received}\n")
                f.write(f"Total Expected Packets: {self.total_expected}\n")
                f.write(f"Missed Packets: {self.missed_packets}\n")
                if self.total_expected > 0:
                    loss_percent = (self.missed_packets / self.total_expected) * 100
                else:
                    loss_percent = 0
                f.write(f"Packet Loss: {loss_percent:.1f}%\n")
                f.write(f"Total Bytes: {self.total_bytes}\n")
                elapsed_sec = max(
                    1, self.total_expected * 3
                )  # same assumption as throughput
                throughput = self.total_bytes / elapsed_sec
                f.write(f"Approx Throughput: {throughput:.1f} B/s\n")
            tk.messagebox.showinfo("Success", f"Performance log saved to {filename}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Could not save log: {e}")

    def save_sensor_csv(self):
        filename = f"sensor_log_{int(time.time())}.csv"
        try:
            with open(filename, "w", newline="") as csvfile:
                fieldnames = ["timestamp", "sensor_value", "is_sensor_valid", "seq"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for entry in self.sensor_log:
                    writer.writerow(entry)
            messagebox.showinfo(
                "Success",
                f"Last {len(self.sensor_log)} sensor readings saved to {filename}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not save CSV: {e}")
