import time
import math
import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
from websocket import create_connection, WebSocketConnectionClosedException
from openpyxl import Workbook

# Data containers for plot points
x, y, z = [], [], []

# Relative positions of the sensors (for visualization)
sensor_offsets = {
    "top_left": [-5, 5, 0],  # Adjust based on actual placement (x, y, z)
    "top_right": [5, 5, 0],
    "bottom_left": [-5, -5, 0],
    "bottom_right": [5, -5, 0],
}

# Limit the number of points to keep the plot responsive
MAX_POINTS = 10000

# WebSocket connection to ESP32
ESP32_WS_URL = "ws://192.168.1.219:81/"  # Replace with your ESP32 WebSocket URL

# Generate a timestamped filename for saving the sensor data
timestamp = time.strftime("%Y%m%d_%H%M%S")
file_name = f"sensor_readings_{timestamp}.xlsx"

# Create a new Excel workbook and worksheet
workbook = Workbook()
worksheet = workbook.active
worksheet.title = "Sensor Data"
# Write the header row
worksheet.append(["timestamp", "distanceTopLeft", "distanceTopRight", "distanceBottomLeft", "distanceBottomRight", "pitch", "roll", "yaw"])

# Attempt to establish WebSocket connection with retry mechanism
def connect_to_esp32():
    while True:
        try:
            print("Attempting to connect to ESP32...")
            ws = create_connection(ESP32_WS_URL)
            print("Connected successfully to ESP32!")
            return ws
        except Exception as e:
            print(f"Error connecting to ESP32: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

# Process and convert sensor data to Cartesian coordinates
def process_data(data):
    distances = {
        "top_left": data['distanceTopLeft'],
        "top_right": data['distanceTopRight'],
        "bottom_left": data['distanceBottomLeft'],
        "bottom_right": data['distanceBottomRight']
    }
    pitch = math.radians(data['pitch'])  # Convert pitch to radians
    roll = math.radians(data['roll'])    # Convert roll to radians
    yaw = math.radians(data['yaw'])      # Convert yaw to radians

    # Rotation matrices for pitch, roll, and yaw
    R_yaw = np.array([
        [math.cos(yaw), -math.sin(yaw), 0],  # Yaw affects rotation around Z-axis
        [math.sin(yaw), math.cos(yaw), 0],
        [0, 0, 1]
    ])
    R_pitch = np.array([
        [math.cos(pitch), 0, math.sin(pitch)],  # Pitch affects rotation around X-axis
        [0, 1, 0],
        [-math.sin(pitch), 0, math.cos(pitch)]
    ])
    R_roll = np.array([
        [1, 0, 0],  # Roll affects rotation around Y-axis
        [0, math.cos(roll), -math.sin(roll)],
        [0, math.sin(roll), math.cos(roll)]
    ])

    # Combined rotation matrix R = R_yaw @ R_pitch @ R_roll
    R = np.dot(R_yaw, np.dot(R_pitch, R_roll))

    # Process each sensor
    new_x, new_y, new_z = [], [], []
    for sensor, offset in sensor_offsets.items():
        distance = distances[sensor]
        # Convert distance to a 3D vector
        D = np.array([distance, 0, 0])  # Distance is along the X-axis initially
        # Apply rotation and offset
        rotated = np.dot(R, D) + offset
        # Append transformed coordinates
        new_x.append(rotated[0])
        new_y.append(rotated[1])
        new_z.append(rotated[2])

    return new_x, new_y, new_z

# Create a 3D plot for real-time data
fig = plt.figure(figsize=(12, 8))  # Increase the size of the figure (optional)
ax = fig.add_subplot(111, projection='3d')

# Initial empty scatter plot
scat = ax.scatter([], [], [], c='blue', marker='o')

# Set labels for axes
ax.set_xlabel('X (cm)')
ax.set_ylabel('Y (cm)')
ax.set_zlabel('Z (cm)')

# Adjust the plot limits to 250 cm
ax.set_xlim(-250, 250)  # Set the X axis limit to 250 cm
ax.set_ylim(-250, 250)  # Set the Y axis limit to 250 cm
ax.set_zlim(-250, 250)  # Set the Z axis limit to 250 cm

# Real-time data update function
def update_plot(frame):
    global x, y, z

    try:
        # Receive data from ESP32
        raw_data = ws.recv()
        data = json.loads(raw_data)  # Parse JSON data from WebSocket

        # Process sensor data into Cartesian coordinates using the received data
        new_x, new_y, new_z = process_data(data)

        # Add new points to the existing data
        x.extend(new_x)
        y.extend(new_y)
        z.extend(new_z)

        # Limit the number of points to avoid overwhelming the plot
        if len(x) > MAX_POINTS:
            x = x[-MAX_POINTS:]
            y = y[-MAX_POINTS:]
            z = z[-MAX_POINTS:]

        # Update the scatter plot with new data points
        scat._offsets3d = (x, y, z)

        # Get the current timestamp
        timestamp = time.time()

        # Save the data to the Excel file
        worksheet.append([
            timestamp,
            data['distanceTopLeft'], data['distanceTopRight'],
            data['distanceBottomLeft'], data['distanceBottomRight'],
            data['pitch'], data['roll'], data['yaw']
        ])
        workbook.save(file_name)  # Save the Excel file after each update

    except WebSocketConnectionClosedException:
        print("WebSocket connection was closed unexpectedly.")
        ws.close()
        return scat,

    except Exception as e:
        print(f"Error receiving or processing data: {e}")
        return scat,

    return scat,

# Establish WebSocket connection
ws = connect_to_esp32()

# Set up the animation function
ani = FuncAnimation(fig, update_plot, frames=100, interval=100, blit=False)

# Show the plot
plt.show()

# Close the Excel file when done (good practice)
workbook.close()
