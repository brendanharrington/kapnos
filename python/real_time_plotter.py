import serial
import re
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np

# Serial Port Configuration
serial_port_1 = '/dev/tty.usbmodem2059325650461'
serial_port_2 = '/dev/tty.usbmodem2077325E50461'
baud_rate = 9600

# Open serial connection
ser_1 = serial.Serial(serial_port_1, baud_rate, timeout=1)
ser_2 = serial.Serial(serial_port_2, baud_rate, timeout=1)

# Data Storage
time_data_1 = []
time_data_2 = []
value_data_1 = []
value_data_2 = []
difference_data = []  
start_time = None

# Figure Setup
plt.ion()
fig, ax = plt.subplots()

# Create three line objects: port1, port2, and difference
line1, = ax.plot([], [], 'b-', linewidth=1.5, label='Port 1')
line2, = ax.plot([], [], 'r-', linewidth=1.5, label='Port 2')
line_diff, = ax.plot([], [], 'g-', linewidth=1.5, label='Difference (1 - 2)')

ax.set_xlabel('Time (s)')
ax.set_ylabel('Value')
ax.set_title('Real-Time Serial Data Plot')
ax.grid(True)
ax.legend()

try:
    while True:
        raw_data_1 = ser_1.readline().decode('utf-8').strip()
        raw_data_2 = ser_2.readline().decode('utf-8').strip()

        # Filter out data packets that contain unwanted characters
        if '[' in raw_data_1 or ']' in raw_data_1:
            continue
        if '[' in raw_data_2 or ']' in raw_data_2:
            continue

        # Extract numeric values from the formatted strings
        match_1 = re.search(r'(\d+):\s*(-?\d+\.\d+|-?\d+)', raw_data_1)
        match_2 = re.search(r'(\d+):\s*(-?\d+\.\d+|-?\d+)', raw_data_2)

        if match_1 and match_2:
            param_id_1 = int(match_1.group(1))
            param_value_1 = float(match_1.group(2))
            param_id_2 = int(match_2.group(1))
            param_value_2 = float(match_2.group(2))

            # Update only if these are the parameters of interest
            if param_id_1 == 3 and param_id_2 == 3:
                if start_time is None:
                    start_time = datetime.datetime.now()

                elapsed_time = (datetime.datetime.now() - start_time).total_seconds()

                # Store data
                time_data_1.append(elapsed_time)
                value_data_1.append(param_value_1)
                time_data_2.append(elapsed_time)
                value_data_2.append(param_value_2)

                # Calculate and store the difference
                diff = param_value_1 - param_value_2
                difference_data.append(diff)

                # Limit stored data to last 100 points
                if len(time_data_1) > 100:
                    time_data_1.pop(0)
                    value_data_1.pop(0)
                if len(time_data_2) > 100:
                    time_data_2.pop(0)
                    value_data_2.pop(0)
                if len(difference_data) > 100:
                    difference_data.pop(0)

                # Update line for Port 1
                line1.set_xdata(time_data_1)
                line1.set_ydata(value_data_1)

                # Update line for Port 2
                line2.set_xdata(time_data_2)
                line2.set_ydata(value_data_2)

                # Update line for difference
                line_diff.set_xdata(time_data_1)  # Or time_data_2 — they are effectively synced
                line_diff.set_ydata(difference_data)

                # Adjust x-axis (last 20 seconds visible)
                ax.set_xlim(max(0, elapsed_time - 20), elapsed_time + 1)

                # Find overall min/max among all three data sets
                combined_min = min(min(value_data_1), min(value_data_2), min(difference_data))
                combined_max = max(max(value_data_1), max(value_data_2), max(difference_data))
                ax.set_ylim(combined_min - 0.5, combined_max + 0.5)

                plt.draw()
                plt.pause(0.05)

except KeyboardInterrupt:
    print("Exiting...")
    ser_1.close()
    ser_2.close()
    plt.ioff()
    plt.show()
