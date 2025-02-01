# Lerobot-SO100-Arm

## 🚀 Train Run Command (for offline files)


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
