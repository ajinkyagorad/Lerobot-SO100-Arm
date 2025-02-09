



import numpy as np
import genesis as gs

# Initialize Genesis
gs.init(backend=gs.cpu)  # Use gs.gpu if you have a compatible GPU

# Create a scene
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(0, -3.5, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=30,
        max_FPS=60,
    ),
    sim_options=gs.options.SimOptions(
        dt=0.01,  # Simulation step time
    ),
    show_viewer=True,
)

# Load the URDF file into Genesis
robot = scene.add_entity(
    gs.morphs.URDF(
        file='./SO-ARM100-main/URDF/SO_5DOF_ARM100_8j_URDF.SLDASM/urdf/SO_5DOF_ARM100_8j_URDF.SLDASM.urdf',
        fixed=True,  # Keep the base fixed to avoid falling
    )
)

# Build the scene
scene.build()

# Define joint names based on URDF
joint_names = [
    "Rotation",      # Base rotation
    "Pitch",         # Upper arm pitch
    "Elbow",         # Lower arm movement
    "Wrist_Pitch",   # Wrist pitch
    "Wrist_Roll",    # Wrist roll
    "Jaw"            # Gripper
]

# Get the local DOF indices for the joints
dof_indices = [robot.get_joint(name).dof_idx_local for name in joint_names]

# Set control gains (PD control)
robot.set_dofs_kp(
    kp=np.array([4500, 4500, 3500, 3500, 2000, 2000]),  # Adjust these values as needed
    dofs_idx_local=dof_indices,
)

robot.set_dofs_kv(
    kv=np.array([450, 450, 350, 350, 200, 200]),
    dofs_idx_local=dof_indices,
)

robot.set_dofs_force_range(
    lower=np.array([-87, -87, -87, -87, -12, -12]),
    upper=np.array([87, 87, 87, 87, 12, 12]),
    dofs_idx_local=dof_indices,
)

# Set initial positions for the joints
target_positions = np.array([0.0, 0.5, -0.5, 0.0, 0.3, 0.1])

# Run the simulation with control
for i in range(500):
    robot.control_dofs_position(target_positions)

    # Step simulation
    scene.step()

    # Gradually move the gripper (Jaw)
    if i % 50 == 0:
        target_positions[-1] = -target_positions[-1]  # Toggle Jaw open/close


# Keep running the simulation indefinitely
try:
    while True:
        scene.step()
except KeyboardInterrupt:
    print("\n[Genesis] Exiting simulation.")