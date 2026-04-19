# Script by Nyoman Yudi Kurniawan © 2025
# www.aisi555.com
# nyomanyudik@gmail.com

import psutil
import os

def kill_python_processes():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if the process name contains "python" (case-insensitive)
            if "python" in proc.info['name'].lower():
                print(f"Terminating Python process: {proc.info['pid']}")
                proc.terminate()  # Gracefully terminate the process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

if __name__ == "__main__":
    kill_python_processes()
