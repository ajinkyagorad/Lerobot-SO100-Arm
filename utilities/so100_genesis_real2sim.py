import numpy as np
import torch
import time
import genesis as gs
from lerobot.common.robot_devices.robots.utils import make_robot_from_config
from lerobot.common.robot_devices.robots.configs import So100RobotConfig

# Flag to switch between simulation and real robot (external arm)
run_in_simulation = True  # Set to True for simulation-only mode

# Load SO-ARM100 Robot Config
robot_config = So100RobotConfig(cameras={})  # Set cameras to an empty dictionary
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


    robot.connect()  # ✅ FIX: Connect before using leader arm
    return scene, robot_sim, robot




scene, robot_sim, robot = initialize_robot()


def follow_leader():
    """
    Reads leader arm's angles and visualizes them in simulation.
    Only updates the simulation without sending actions to the follower arm.
    """
    print("Following leader arm's movement...")

    while True:
        # Read leader arm's joint angles
        leader_pos = robot.leader_arms["main"].read("Present_Position")  # Read from leader
        leader_pos = [0, 90, -90, -90, 90, 0] + [-1, -1, 1, 1, 1, 1] * leader_pos
        print(["{:.2f}".format(x) for x in leader_pos])
        leader_pos = torch.from_numpy(leader_pos)  # Convert to torch tensor
        
        # Convert to radians
        target_angles = leader_pos * np.pi / 180
        target_angles = target_angles.numpy()  # Convert to NumPy

        # Apply angles directly to simulation
        robot_sim.control_dofs_position(target_angles)

        # Step the simulation
        scene.step()


# Start following leader arm
follow_leader()
