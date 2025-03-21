# Handheld-3D-Ultrasonic-Mapper

## Description
The **Handheld 3D Ultrasonic Mapper** is a real-time mapping device that uses an **ESP32 microcontroller** with **HC-SR04 ultrasonic sensors** and an **MPU6050 IMU** to capture 3D spatial data. The system transmits sensor data via **WebSockets**, and a **Python-based visualization tool** processes and plots the data in a **3D interactive graph**.

## Features
- **ESP32-based WebSocket communication**
- **HC-SR04 ultrasonic sensors** for distance measurement
- **MPU6050 IMU** for orientation tracking (pitch, roll, yaw)
- **Real-time 3D visualization** using Python & Matplotlib
- **Data logging in Excel format (.xlsx)**
- **Automatic reconnection on WebSocket failure**

## Hardware Requirements
- **ESP32 Development Board**
- **4x HC-SR04 Ultrasonic Sensors**
- **MPU6050 Accelerometer & Gyroscope Module**
- **Jumper Wires & Breadboard**

## Software Requirements
- **Arduino IDE (or PlatformIO in VS Code)**
- **Python 3.7+**
- **VS Code (for development & Git integration)**
- **Git (for version control)**

## Libraries & Dependencies
### **Arduino Libraries (Install via Library Manager)**
- `WiFi.h` (Built-in for ESP32)
- `WebSocketsServer.h`
- `Wire.h`
- `Adafruit_MPU6050.h`
- `Adafruit_Sensor.h`

### **Python Dependencies**
Install required Python packages using:
```bash
pip install numpy matplotlib openpyxl websocket-client
```

## Installation & Setup
### **1. Clone the Repository**
```bash
git clone https://github.com/Lithishc/Handheld-3D-Ultrasonic-Mapper.git
cd Handheld-3D-Ultrasonic-Mapper
```

### **2. Flash ESP32 Code**
- Open `esp32_code.ino` in **Arduino IDE**
- Configure **WiFi credentials** (`ssid` & `password`)
- Select **ESP32 Dev Module** as the board
- Compile & upload to the ESP32

### **3. Run the Python Visualization Script**
```bash
python visualizer.py
```

## Usage
1. Power on the ESP32 and connect it to WiFi.
2. Run the **Python visualization script** to receive real-time data.
3. Observe the **3D plot** updating dynamically.

## Troubleshooting
### **ESP32 Not Connecting to WiFi**
- Ensure correct WiFi credentials in `esp32_code.ino`.
- Restart ESP32 and check the serial monitor.

### **WebSocket Connection Fails**
- Ensure ESP32 is running and connected.
- Verify the WebSocket URL in `visualizer.py`.

### **Python Errors (Missing Modules)**
- Ensure dependencies are installed using `pip install -r requirements.txt`.

## Contribution
Feel free to **fork** the repository, create a **pull request**, or open an **issue** for improvements!

## License
This project is licensed under the **MIT License**.

