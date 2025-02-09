import numpy as np
import torch
import time
import genesis as gs
from lerobot.common.robot_devices.robots.utils import make_robot_from_config
from lerobot.common.robot_devices.robots.configs import So100RobotConfig
# send action has angles in degrees, but currently, it does not work properly as there is offset of position, i.e. model sim angles need to be mapped to real-world angles before
# Flag to switch between simulation and real robot (external arm)
run_in_simulation = False  # Set to True for simulation-only mode

# Load SO-ARM100 Robot Config
robot_config = So100RobotConfig(cameras={})  # Set cameras to an empty dictionary#print(vars(robot_config))
robot = make_robot_from_config(config=robot_config)

# Function to initialize the robot (simulation or real)
def initialize_robot():
    # Initialize Genesis Simulation (for both modes)
    gs.init(backend=gs.cpu)
    scene = gs.Scene(show_viewer=True)

    # Load the URDF File for simulation
    robot_sim = scene.add_entity(
        gs.morphs.URDF(
            file='utilities/SO-ARM100-main/URDF/SO_5DOF_ARM100_8j_URDF.SLDASM/urdf/SO_5DOF_ARM100_8j_URDF.SLDASM.urdf',
            fixed=True,
        )
    )

    # Build the Scene
    scene.build()
    print(f"DOFs in robot: {robot_sim.n_dofs}")

    if not run_in_simulation:
        # Connect real robot only in non-simulation mode
        robot.connect()
        return scene, robot_sim, robot

    return scene, robot_sim


# Run the initialization
if run_in_simulation:
    scene, robot_sim = initialize_robot()
else:
    scene, robot_sim, robot = initialize_robot()

def move_to_angles(target_angles, steps=100, duration=2.0):
    """
    Moves the robot to the target angles smoothly over a given number of steps.
    
    :param target_angles: Target joint angles in radians.
    :param steps: Number of interpolation steps.
    :param duration: Total time to complete the movement (in seconds).
    """
    print(f"Moving to: {np.degrees(target_angles)} degrees smoothly")

    # Get current joint positions (Convert to NumPy for calculations)
    current_angles = robot_sim.get_dofs_position().cpu().numpy()

    # Convert target_angles to NumPy array if it's a tensor
    if isinstance(target_angles, torch.Tensor):
        target_angles = target_angles.cpu().numpy()

    # Interpolate between current and target angles
    for i in range(steps + 1):
        interp_angles = current_angles + (target_angles - current_angles) * (i / steps)
        
        # Apply interpolated angles to simulation
        robot_sim.control_dofs_position(interp_angles)

        if not run_in_simulation:
            # Convert radians to expected motor range
            action = np.array([-1, -1, 1, 1, 1, 1]) * interp_angles * 180 / np.pi + np.array([0, 87, 75, 97, -12, 0])
            action_tensor = torch.tensor(action, dtype=torch.float32)
            robot.send_action(action_tensor)

        # Step the simulation
        scene.step()

        # Adjust sleep duration for smooth movement
        time.sleep(duration / steps)



# Example usage
home_position = np.zeros(robot_sim.n_dofs)  # Assuming the robot is in home position (all angles = 0)
print("Moving to home position...")
move_to_angles(home_position)
time.sleep(5)  # Delay for visual feedback

# Optionally, move to random positions
for _ in range(5):
    target = np.random.uniform(-1.5, 1.5, robot_sim.n_dofs)
    move_to_angles(target)
    time.sleep(6)  # Delay between moves

# Keep Simulation Running
try:
    while True:
        scene.step()
except KeyboardInterrupt:
    print("\n[Genesis] Exiting simulation.")
    if not run_in_simulation:
        robot.disconnect()
