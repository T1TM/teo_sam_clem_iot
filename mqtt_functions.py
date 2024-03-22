import time
import paho.mqtt.publish as publish

def function_a():
    print("Function A was called.")
    return "Function A executed successfully."

def function_b():
    print("Function B was called.")
    return "Function B executed successfully."

def move_forward():
    print("Moving forward")
    publish.single("ecar/robot/command", "Z", hostname="test.mosquitto.org")
    time.sleep(5)
    publish.single("ecar/robot/command", "P", hostname="test.mosquitto.org")
    return "success car command forwards sent"

def move_backward():
    print("Moving backward")
    publish.single("ecar/robot/command", "S", hostname="test.mosquitto.org")
    time.sleep(1)
    publish.single("ecar/robot/command", "P", hostname="test.mosquitto.org")
    return "success car command back sent"

def move_left():
    print("Turning left")
    publish.single("ecar/robot/command", "Q", hostname="test.mosquitto.org")
    time.sleep(0.2)
    publish.single("ecar/robot/command", "P", hostname="test.mosquitto.org")
    return "success car command left sent"

def move_right():
    print("Turning right")
    publish.single("ecar/robot/command", "D", hostname="test.mosquitto.org")
    time.sleep(0.2)
    publish.single("ecar/robot/command", "P", hostname="test.mosquitto.org")
    return "success car command right sent"

def move_stop():
    print("Turning stop")
    publish.single("ecar/robot/command", "P", hostname="test.mosquitto.org")
    return "success car command stop sent"