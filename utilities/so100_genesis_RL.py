import numpy as np
import genesis as gs
import gym
from stable_baselines3 import PPO

# ✅ Initialize Genesis
gs.init(backend=gs.cpu)

# ✅ Create a simulation scene
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(),
    sim_options=gs.options.SimOptions(dt=0.01),
)

# ✅ Load the URDF model
robot = scene.add_entity(
    gs.morphs.URDF(
        file="./SO-ARM100-main/URDF/SO_5DOF_ARM100_8j_URDF.SLDASM/urdf/SO_5DOF_ARM100_8j_URDF.SLDASM.urdf",
        fixed=True,
    )
)

# ✅ Build the scene
scene.build()


# ✅ Define a custom RL environment
class GenesisArmEnv(gym.Env):
    def __init__(self):
        super(GenesisArmEnv, self).__init__()
        self.action_space = gym.spaces.Box(low=-1.0, high=1.0, shape=(5,), dtype=np.float32)  # 5DOF Arm
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(6,), dtype=np.float32)  # XYZ + angles
        self.target_pos = np.array([0.3, 0.2, 0.5])  # Move to (x=0.3, y=0.2, z=0.5)

    def step(self, action):
        #print(f"DOFs in robot: {robot.n_dofs}")  # ✅ Debugging info
        #print(f"Action shape: {action.shape}")

        # ✅ Ensure action matches DOFs count
        action_padded = np.pad(action, (0, robot.n_dofs - len(action)))

        # ✅ Apply control to the robot
        robot.control_dofs_position(action_padded * np.pi)

        scene.step()  # Step the simulation

        # ✅ Fix end effector position retrieval
        end_effector_pos = robot.get_link("Fixed_Jaw").get_pos()

        # ✅ Ensure state matches expected observation space shape (6,)
        state = np.concatenate((end_effector_pos[:3], action_padded[:3]))  # ✅ Keep only 6 values

        # Reward is negative distance to target
        reward = -np.linalg.norm(end_effector_pos - self.target_pos)
        done = np.linalg.norm(end_effector_pos - self.target_pos) < 0.01  # Stop when close

        return state, reward, done, {}


    def reset(self):
        return np.zeros(6)  # Reset state

# ✅ Create environment
env = GenesisArmEnv()

# ✅ Train using PPO
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=50000)

# ✅ Run the trained policy
obs = env.reset()
for _ in range(500):
    action, _states = model.predict(obs)
    obs, reward, done, _ = env.step(action)
    if done:
        break
