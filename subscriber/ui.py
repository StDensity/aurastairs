import tkinter as tk


class SubscriberUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AuraStairs – Motion Monitor")
        self.root.geometry("320x200")
        self.root.resizable(False, False)

        self.status_label = tk.Label(root, text="Status: DISCONNECTED")
        self.status_label.pack(pady=5)

        self.motion_label = tk.Label(root, text="Motion: UNKNOWN", font=("Arial", 16))
        self.motion_label.pack(pady=10)

        self.error_label = tk.Label(root, text="Error: NONE")
        self.error_label.pack(pady=5)

        self.canvas = tk.Canvas(root, width=60, height=60)
        self.canvas.pack(pady=10)
        self.indicator = self.canvas.create_oval(10, 10, 50, 50, fill="gray")

    def update_from_data(self, data):
        """
        Called from MQTT thread → schedule UI update safely
        """
        self.root.after(0, self._update_ui, data)

    def _update_ui(self, data):
        sensor_value = data.get("sensor_value", 0)
        is_sensor_valid = data.get("is_sensor_valid", False)

        self.status_label.config(text="Status: CONNECTED")

        if sensor_value:
            self.motion_label.config(text="Motion: YES")
            self.canvas.itemconfig(self.indicator, fill="green")
        else:
            self.motion_label.config(text="Motion: NO")
            self.canvas.itemconfig(self.indicator, fill="red")

        self.error_label.config(text=f"Error: {is_sensor_valid}")
