"""
Multimodal OR Sensor testing file to measure the accuracy and the
detection of a car in the bay. We will use this file to test a toy
car and a real car.

This is an OR test - if both sensors detect a car in the bay,
the LED will turn from Green (free) to Red (occupied)

Components required:
x1 Raspberry Pi Kit (RPI, cables, power source, breadboard etc.)
x1 5mm Red LED GPIO 
x1 5mm Green LED
x2 330 ohm resistors
x1 Ultrasonic Sensor

Code description:
File to test the ultrasonic sensor measurement accuracy, prints out
value when the code is run:
- Distance measured when bay is occupied
- Distance measured when bay is free
- % Accuracy with actual (ground truth) measured using measuring
tape or micrometer.
--------------------------------------------------------------------
Setup:
Will need to create a circuit diagram for the connection of
ultrasonic sensor and 2 LEDs.

Ensure the Ultrasonic sensor is connected as described:
• VCC connects to Pin 2 (5V)
• Trig connects to GPIO Pin 8
• Echo connects to R1 (1k OHM)
• R2 and R3 (1k OHM + 1 k OHM) connects from R1 to Ground
• Wire from R1 and R2+R3 connects to GPIO Pin 7
• GND connects to Pin 34 (Ground)

LED(GPIO 5) - Green LED
LED(GPIO 6) - Red LED
--------------------------------------------------------------------

Date: 10/10/2023
Author: Asad Maza - Group 3
"""
# Imports
import RPi.GPIO as GPIO
import time
import json
from gpio_reset import all_pins_to_off
from PiicoDev_QMC6310 import PiicoDev_QMC6310
from PiicoDev_Unified import sleep_ms


# Define distance measuring function
def read_distance(TRIG, ECHO):
    GPIO.output(TRIG, False)
    time.sleep(1.5) # changed sleep time to read faster.
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)    
    while GPIO.input(ECHO)==0:
        pulse_start = time.time()
    while GPIO.input(ECHO)==1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 34300) / 2
    distance = round(distance, 2)
    return distance

# GPIO config
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(7, GPIO.IN)
green_LED = GPIO.output(5, GPIO.HIGH)
red_LED = GPIO.output(6, GPIO.LOW)

# Mapping bay information
bay_mapping = {
    'Bay1': {'red_led': 6, 'yellow_or_green_led': 5,
             'sensor_trigger': 8, 'sensor_echo': 7, 'shared_state' : 0,
             'state': 0, 'prev_state': 0,
             'bay_type': 'reserved', 'is_bay_booked' : 0}
    }

# Initialise interval variables for publish and check bay status and threshold for distance
check_bay_status_interval = 0.5  # Queries bay status every (1.5 + 0.5) seconds
last_publish_time = time.time()
last_check_time = time.time()

threshold_max = 20.0 # in cm
threshold_min = 0.0 # in cm

# initalise continue_loop to Yes
continue_loop = "Yes"

# Initialise threshold value
sensor_threshold = 0.01 # in percent (e.g. 10% = 0.10)

base_val_threshold = 0.08 # in percent (e.g. 2% = 0.02)
# Initialise sensor
magSensor = PiicoDev_QMC6310(range=3000)
def get_average(data_list):
    return sum(data_list) / len(data_list)

def collect_data_for_seconds(seconds):
    data_list = []
    for _ in range(seconds):
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']
        data_list.append(z_axis_strength)
        sleep_ms(1000)
    return data_list


# Loop until a valid default value is obtained
while True:
    # Read the data of the previous ten seconds
    data_list = collect_data_for_seconds(10)
    
    # If the data fluctuation is less than 2%, set it as the default value
    avg_value = get_average(data_list)
    max_value = max(data_list)
    min_value = min(data_list)
    fluctuation = (max_value - min_value) / avg_value
    
    if fluctuation < base_val_threshold:
        default_value = avg_value
        break

print("Average default value for magnetosensor:", default_value)

try:
    initial_publish = True # Flag to force initial publish
    state_changed = False  # Flag to indicate whether state has changed
    
    while continue_loop == "Yes":
        current_time = time.time()
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']                    
        # Check status of each bay if enough time has elapsed since the last check
        if current_time - last_check_time >= check_bay_status_interval:
            last_check_time = current_time
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            for bay, info in bay_mapping.items():
                dist_measured = read_distance(info['sensor_trigger'], info['sensor_echo'])
                # Remember previous state
                info['prev_state'] = info['state']
                # if ultrasonic detects something
                if dist_measured <= threshold_max and dist_measured >= threshold_min :
                    # if magnetometer detects something
                    print("ultrasonic sensor is detecting something dist_measured: " + str(dist_measured) + " bay status is occupied")
                    if abs((z_axis_strength - default_value) / default_value) > sensor_threshold:
                        print("magnetometer is detecting something  bay status is occupied ")
                        print("magnetometer difference :"+ str((z_axis_strength - default_value) / default_value))
                        print("Z-axis strength:", z_axis_strength)
                        print("detected car")
                        if info['state'] == 0:
                            info['state'] = 1
                            state_changed = True  # State has changed
                            green_LED = GPIO.output(5, GPIO.LOW)
                            red_LED = GPIO.output(6, GPIO.HIGH)
                    # if not
                    else:
                        print("magnetometer is not detecting anything bay status is still occupied ")
                        print("magnetometer difference :"+ str((z_axis_strength - default_value) / default_value))
                        print("Z-axis strength:", z_axis_strength)
                        print("detected car")
                        if info['state'] == 0:
                            info['state'] = 1
                            state_changed = True  # State has changed
                            green_LED = GPIO.output(5, GPIO.LOW)
                            red_LED = GPIO.output(6, GPIO.HIGH)
                # if not
                else:
                    # if magnetometer detects something
                    print("ultrasonic sensor is not detecting anything dist_measured: " + str(dist_measured) + " bay status not occupied")
                    if abs((z_axis_strength - default_value) / default_value) > sensor_threshold:
                        print("magnetometer is detecting something bay status is occupied ")
                        print("magnetometer difference :"+ str((z_axis_strength - default_value) / default_value))
                        print("Z-axis strength:", z_axis_strength)
                        print("detected car")
                        if info['state'] == 0:
                            info['state'] = 1
                            state_changed = True  # State has changed
                            green_LED = GPIO.output(5, GPIO.LOW)
                            red_LED = GPIO.output(6, GPIO.HIGH)
                    # if not
                    else:
                        print("magnetometer is not detecting anything bay status is not occupied ")
                        print("magnetometer difference :"+ str((z_axis_strength - default_value) / default_value))
                        print("Z-axis strength:", z_axis_strength)
                        print("no car")
                        if info['state'] == 1:
                            info['state'] = 0
                            state_changed = True  # State has changed
                            green_LED = GPIO.output(5, GPIO.HIGH)
                            red_LED = GPIO.output(6, GPIO.LOW)
                        
                
                
                continue_loop = "No"
                continue_loop = input("Do you require another reading? -Please reply with Yes")
                
except KeyboardInterrupt:
    print("Terminating and cleaning up")
    all_pins_to_off()
