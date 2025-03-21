#include <WiFi.h>
#include <WebSocketsServer.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

// Replace with your network credentials
const char* ssid = "your_ssid";
const char* password = "your_password";

// WebSocket server on port 81
WebSocketsServer webSocket = WebSocketsServer(81);

// Adafruit MPU6050 object
Adafruit_MPU6050 mpu;

// HC-SR04 ultrasonic sensor pins
#define TRIG_TOP_LEFT 12
#define ECHO_TOP_LEFT 14
#define TRIG_TOP_RIGHT 27
#define ECHO_TOP_RIGHT 26
#define TRIG_BOTTOM_LEFT 33
#define ECHO_BOTTOM_LEFT 25
#define TRIG_BOTTOM_RIGHT 35
#define ECHO_BOTTOM_RIGHT 32

void setup() {
    Serial.begin(115200);

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Initialize WebSocket
    webSocket.begin();

    // Initialize ultrasonic sensor pins
    pinMode(TRIG_TOP_LEFT, OUTPUT);
    pinMode(ECHO_TOP_LEFT, INPUT);
    pinMode(TRIG_TOP_RIGHT, OUTPUT);
    pinMode(ECHO_TOP_RIGHT, INPUT);
    pinMode(TRIG_BOTTOM_LEFT, OUTPUT);
    pinMode(ECHO_BOTTOM_LEFT, INPUT);
    pinMode(TRIG_BOTTOM_RIGHT, OUTPUT);
    pinMode(ECHO_BOTTOM_RIGHT, INPUT);

    // Initialize I2C for MPU6050 (SDA = GPIO16, SCL = GPIO17)
    Wire.begin(17, 16);
    if (!mpu.begin()) {
        Serial.println("MPU6050 connection failed.");
        while (1);
    }
    Serial.println("MPU6050 connected successfully!");
}

// Function to get distance from an HC-SR04 sensor
float getDistance(int trigPin, int echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    long duration = pulseIn(echoPin, HIGH);
    return duration * 0.0343 / 2;  // Convert time to distance in cm
}

void loop() {
    // Handle WebSocket communication
    webSocket.loop();

    // Measure distances from ultrasonic sensors
    float distanceTopLeft = getDistance(TRIG_TOP_LEFT, ECHO_TOP_LEFT);
    float distanceTopRight = getDistance(TRIG_TOP_RIGHT, ECHO_TOP_RIGHT);
    float distanceBottomLeft = getDistance(TRIG_BOTTOM_LEFT, ECHO_BOTTOM_LEFT);
    float distanceBottomRight = getDistance(TRIG_BOTTOM_RIGHT, ECHO_BOTTOM_RIGHT);

    // Read accelerometer and gyroscope data from MPU6050
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    // Create a JSON-formatted string containing sensor data
    String data = "{";
    data += "\"distanceTopLeft\":" + String(distanceTopLeft) + ",";
    data += "\"distanceTopRight\":" + String(distanceTopRight) + ",";
    data += "\"distanceBottomLeft\":" + String(distanceBottomLeft) + ",";
    data += "\"distanceBottomRight\":" + String(distanceBottomRight) + ",";
    data += "\"accelX\":" + String(a.acceleration.x) + ",";
    data += "\"accelY\":" + String(a.acceleration.y) + ",";
    data += "\"accelZ\":" + String(a.acceleration.z) + ",";
    data += "\"gyroX\":" + String(g.gyro.x) + ",";
    data += "\"gyroY\":" + String(g.gyro.y) + ",";
    data += "\"gyroZ\":" + String(g.gyro.z) + "}";

    // Broadcast sensor data to all connected WebSocket clients
    webSocket.broadcastTXT(data);

    delay(5); // Short delay to prevent overwhelming the WebSocket server
}
