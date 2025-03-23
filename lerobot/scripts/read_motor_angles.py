import time
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus

# Define port and model
PORT = "COM10"  # Update this to your actual port
MODEL = "sts3215"

# Define motor IDs and names
motor_ids = list(range(1, 8))  # IDs 1 to 7
motor_names = [f"motor_{i}" for i in motor_ids]
motors = {name: (idx, MODEL) for name, idx in zip(motor_names, motor_ids)}

# Initialize and connect motor bus
bus = FeetechMotorsBus(port=PORT, motors=motors)
bus.connect()
bus.set_bus_baudrate(1_000_000)

try:
    while True:
        positions = bus.read("Present_Position", motor_names)
        print("Raw Motor Positions (steps):", positions)
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Stopped reading motor positions.")
finally:
    bus.disconnect()
