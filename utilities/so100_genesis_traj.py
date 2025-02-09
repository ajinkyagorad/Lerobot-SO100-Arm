import numpy as np
import genesis as gs

# Initialize Genesis
gs.init(backend=gs.cpu)

# Create a scene
scene = gs.Scene(show_viewer=True)

# Load the URDF file
robot = scene.add_entity(
    gs.morphs.URDF(
        file='./utilities/SO-ARM100-main/URDF/SO_5DOF_ARM100_8j_URDF.SLDASM/urdf/SO_5DOF_ARM100_8j_URDF.SLDASM.urdf',
        fixed=True,
    )
)

# Build the scene
scene.build()

# Print DOF info
print(f"DOFs in robot: {robot.n_dofs}")

# Define waypoints for the end-effector (joint angles instead of XYZ)
waypoints = [
    np.zeros(robot.n_dofs),                # Initial position
    np.random.uniform(-1, 1, robot.n_dofs), # Random position 1
    np.random.uniform(-1, 1, robot.n_dofs), # Random position 2
    np.random.uniform(-1, 1, robot.n_dofs), # Random position 3
]

# Follow the trajectory
for target_position in waypoints:
    print(f"Moving to: {target_position}")
    robot.control_dofs_position(target_position)  # Control joints instead
    for _ in range(50):  # Give time for movement
        scene.step()

# Keep running the simulation
try:
    while True:
        scene.step()
except KeyboardInterrupt:
    print("\n[Genesis] Exiting simulation.")
