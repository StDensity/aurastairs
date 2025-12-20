"""Utility functions for Subscriber UI."""

import tkinter as tk
from tkinter import messagebox
import csv
import time
import os


def ensure_logs_folder(folder_name="logs"):
    """Ensure logs folder exists, create if necessary."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name


def save_sensor_csv(filename, sensor_log, folder="logs"):
    """Save sensor log to CSV file in logs folder."""
    ensure_logs_folder(folder)
    filepath = os.path.join(folder, filename)
    try:
        with open(filepath, "w", newline="") as csvfile:
            fieldnames = ["timestamp", "sensor_value", "is_sensor_valid", "seq"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for entry in sensor_log:
                writer.writerow(entry)
        messagebox.showinfo(
            "Success",
            f"Last {len(sensor_log)} sensor readings saved to {filepath}",
        )
    except Exception as e:
        messagebox.showerror("Error", f"Could not save CSV: {e}")


def save_perf_log(
    filename, total_received, total_expected, missed_packets, total_bytes, folder="logs"
):
    """Save performance test log to file in logs folder."""
    ensure_logs_folder(folder)
    filepath = os.path.join(folder, filename)
    try:
        with open(filepath, "w") as f:
            f.write("Performance Test Log\n")
            f.write(f"Total Received Packets: {total_received}\n")
            f.write(f"Total Expected Packets: {total_expected}\n")
            f.write(f"Missed Packets: {missed_packets}\n")
            if total_expected > 0:
                loss_percent = (missed_packets / total_expected) * 100
            else:
                loss_percent = 0
            f.write(f"Packet Loss: {loss_percent:.1f}%\n")
            f.write(f"Total Bytes: {total_bytes}\n")
            elapsed_sec = max(1, total_expected * 3)  # 3s publisher interval assumed
            throughput = total_bytes / elapsed_sec
            f.write(f"Approx Throughput: {throughput:.1f} B/s\n")
        messagebox.showinfo("Success", f"Performance log saved to {filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save log: {e}")


def calculate_perf_metrics(missed_packets, total_expected, total_bytes):
    """Calculate performance metrics."""
    loss_percent = (missed_packets / total_expected) * 100 if total_expected > 0 else 0
    elapsed_sec = max(1, total_expected * 3)  # 3s publisher interval assumed
    throughput = total_bytes / elapsed_sec
    return loss_percent, throughput
