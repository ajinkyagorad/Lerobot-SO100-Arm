import time
import numpy as np
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus, convert_degrees_to_steps

# Define port and model
PORT = "COM12"  # Change to your port
MODEL = "sts3215"

# Define motor IDs and desired angles (degrees) for each motor
motor_ids = list(range(1, 8))  # IDs 1 to 7
motor_names = [f"motor_{i}" for i in motor_ids]
desired_angles_deg = [180,180,180,180,180,180,180]  # Customize this list

# Create motors dictionary for FeetechMotorsBus
motors = {name: (idx, MODEL) for name, idx in zip(motor_names, motor_ids)}

# Initialize and connect motor bus
bus = FeetechMotorsBus(port=PORT, motors=motors)
bus.connect()
bus.set_bus_baudrate(1_000_000)  # Or match your actual baudrate

# Convert degrees to motor steps
steps = convert_degrees_to_steps(np.array(desired_angles_deg), [MODEL] * 7)
print(steps)
# Write goal positions
bus.write("Goal_Position", steps, motor_names)

# Optionally verify written positions
time.sleep(0.5)
positions = bus.read("Present_Position", motor_names)
print("Current positions (after command):", positions)

bus.disconnect()
