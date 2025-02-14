import serial
import re
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np

# Serial Port Configuration
serial_port = '/dev/tty.usbmodem2059325650461'  # CHANGE TO CORRECT PORT
baud_rate = 9600

# Open serial connection
ser = serial.Serial(serial_port, baud_rate, timeout=1)

# Data Storage
time_data = []
value_data = []
start_time = None

# Figure Setup
plt.ion()
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b', linewidth=1.5)
ax.set_xlabel('Time (s)')
ax.set_ylabel('Value')
ax.set_title('Real-Time Serial Data Plot')
ax.grid(True)

# Real-Time Data Acquisition
try:
    while True:
        raw_data = ser.readline().decode('utf-8').strip()  # Read incoming data as a line
        
        if '[' in raw_data or ']' in raw_data:  # Detect start/end of a new data packet
            continue

        # Extract numeric values from the formatted string
        match = re.search(r'(\d+):\s*(-?\d+\.\d+|-?\d+)', raw_data)
        
        if match:
            param_id = int(match.group(1))  # Extract parameter ID
            param_value = float(match.group(2))  # Extract parameter value

            if param_id == 3:  # Change this to the ID you want to track
                if start_time is None:
                    start_time = datetime.datetime.now()
                
                elapsed_time = (datetime.datetime.now() - start_time).total_seconds()
                time_data.append(elapsed_time)
                value_data.append(param_value)

                # Limit stored data to the last 100 points for better performance
                if len(time_data) > 100:
                    time_data.pop(0)
                    value_data.pop(0)

                # Update Plot
                line.set_xdata(time_data)
                line.set_ydata(value_data)
                ax.set_xlim(max(0, elapsed_time - 20), elapsed_time + 1)  # Keep the last 20s visible
                ax.set_ylim(min(value_data) - 1, max(value_data) + 1)
                plt.draw()
                plt.pause(0.05)  # Reduced pause time for smoother updates

except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
    plt.ioff()
    plt.show()
