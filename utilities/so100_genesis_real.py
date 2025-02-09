import numpy as np
import genesis as gs
import serial
import time

# ✅ Initialize Genesis Simulation
gs.init(backend=gs.cpu)
scene = gs.Scene(show_viewer=True)

# ✅ Load the follower arm URDF
robot = scene.add_entity(
    gs.morphs.URDF(
        file="./SO-ARM100-main/URDF/SO_5DOF_ARM100_8j_URDF.SLDASM/urdf/SO_5DOF_ARM100_8j_URDF.SLDASM.urdf",
        fixed=True,
    )
)
scene.build()

# ✅ Connect to Feetech Servo Controller
SERIAL_PORT = "/dev/ttyUSB0"  # Update this as per your system
BAUD_RATE = 115200
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Connected to Feetech Controller")
except Exception as e:
    print(f"[ERROR] Cannot connect to Feetech: {e}")
    ser = None  # Simulation will continue if real hardware fails

# ✅ Define a simple trajectory (XYZ Positions)
waypoints = [
    np.array([0.2, 0.1, 0.3]),
    np.array([0.3, 0.2, 0.5]),
    np.array([0.1, -0.1, 0.4]),
    np.array([0.2, 0.0, 0.6]),
]

# ✅ Convert XYZ to joint angles (dummy function for now)
def inverse_kinematics(target_pos):
    return np.random.uniform(-1.0, 1.0, size=(6,))  # Replace with real IK solver

# ✅ Send command to Feetech servos
def send_command_to_real_robot(joint_angles):
    if ser is None:
        return  # Skip if no serial connection
    
    command = f"#{joint_angles[0]:.2f},{joint_angles[1]:.2f},{joint_angles[2]:.2f}\n"
    ser.write(command.encode())
    time.sleep(0.02)  # Allow time for motors to process

# ✅ Follow the trajectory
for target_position in waypoints:
    joint_positions = inverse_kinematics(target_position)
    print(f"Moving to {target_position}, Joint Angles: {joint_positions}")
    
    # ✅ Move in Genesis Simulation
    robot.control_dofs_position(joint_positions)
    
    # ✅ Send commands to the real robot
    send_command_to_real_robot(joint_positions)
    
    # ✅ Step simulation to allow movement
    for _ in range(50):
        scene.step()

# ✅ Keep simulation running
try:
    while True:
        scene.step()
except KeyboardInterrupt:
    print("\n[Genesis] Exiting simulation.")
    if ser:
        ser.close()
