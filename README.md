# Lerobot-SO100-Arm
### Training Visualization and Evaluation Examples(for offline mode)

### 🚀 Train Run Command 


This command initiates the training process using the `so100_real` environment and the `act_so100_real` policy on a CUDA device. Issue with 1.6v, so it forces to 2.0, some parts in code also need commenting out which check that.

```bash
python lerobot/scripts/train.py \
  dataset_repo_id=user1234/project_xyz \
  env=so100_real \
  policy=act_so100_real \
  device=cuda \
  wandb.enable=false \
  +dataset.root=/home/username/.cache/huggingface/lerobot/user1234/project_xyz \
  +dataset.local_files_only=true \
  +dataset.meta._version="v2.0"
```


#### Visualize Dataset
```bash
python lerobot/scripts/visualize_dataset_html.py --repo-id <your_repo_id>/test_dataset --local-files-only 1
```

**Explanation:**
- `--repo-id <your_repo_id>/test_dataset`: Replace `<your_repo_id>` with your dataset repository ID.
- `--local-files-only 1`: Ensures data is accessed locally without online fetching.

#### Record Data for Robot Evaluation
```bash
python lerobot/scripts/control_robot.py record --robot-path lerobot/configs/robot/so100.yaml --fps 30 --repo-id <your_repo_id>/evaluation_dataset --tags so100 tutorial evaluation --warmup-time-s 0 --episode-time-s 400 --reset-time-s 10 --num-episodes 2 --single-task "Put the black tape in white tape" -p outputs/train/2025-01-31/17-32-31_real_world_act_default/checkpoints/160000/pretrained_model/
```

**Explanation:**
- `--robot-path lerobot/configs/robot/so100.yaml`: Path to the robot's configuration file.
- `--fps 30`: Frames per second for data recording.
- `--repo-id <your_repo_id>/evaluation_dataset`: Replace `<your_repo_id>` with your evaluation repository ID.
- `--tags so100 tutorial evaluation`: Tags to classify the data.
- `--warmup-time-s 0`: Time (in seconds) for the robot to warm up.
- `--episode-time-s 400`: Duration (in seconds) of each episode.
- `--reset-time-s 10`: Time (in seconds) between resets.
- `--num-episodes 2`: Number of episodes to record.
- `--single-task "Put the black tape in white tape"`: Specifies the task for the robot.
- `-p outputs/train/2025-01-31/17-32-31_real_world_act_default/checkpoints/160000/pretrained_model/`: Path to the pretrained model for evaluation.

Replace placeholders like `<your_repo_id>` with actual repository IDs as needed.

