#!/usr/bin/env python3
"""
Reads raw Feetech motor step values from multiple ports and motor groups.

Usage:
    python read_motor_angles.py --group "(/dev/ttyUSB0, 1,2,3)" --group "(/dev/ttyUSB1, 4,5)"

Each --group argument should be a tuple-like string:
    "(port, motor_id1, motor_id2, ...)"

    python lerobot/scripts/read_motor_angles.py \
  --group "('/dev/tty_left_follower', 1,2,3,4,5,6)" \
  --group "('/dev/tty_left_leader', 1,2,3,4,5,6)" \
  --group "('/dev/tty_right_follower', 1,2,3,4,5,6,7)" \
  --group "('/dev/tty_right_leader', 1,2,3,4,5,6,7)"

"""

import argparse
import time
import threading
import ast
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig

MODEL = "sts3215"

def monitor_group(port, motor_ids, index, print_lock):
    motor_names = [f"{port}_motor_{i}" for i in motor_ids]
    motors = {name: (idx, MODEL) for name, idx in zip(motor_names, motor_ids)}
    config = FeetechMotorsBusConfig(port=port, motors=motors)
    bus = FeetechMotorsBus(config=config)

    try:
        bus.connect()
        bus.set_bus_baudrate(1_000_000)

        while True:
            steps = bus.read("Present_Position", motor_names)
            with print_lock:
                # Move cursor up to the group's assigned line
                print(f"\033[{5 - index}A", end="")  # Move up (4-index) lines
                print(f"\033[K[{port}] Steps: {steps}")  # Clear line and print
                print(f"\033[{5 - index}B", end="")  # Move cursor back down
            time.sleep(0.05)

    except KeyboardInterrupt:
        with print_lock:
            print(f"\033[{5 - index}A\033[KStopped reading from {port}\033[{5 - index}B")
    finally:
        bus.disconnect()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", action="append", required=True,
                        help='Motor group in format: "(/dev/ttyUSB0, 1,2,3)"')
    args = parser.parse_args()

    threads = []
    print_lock = threading.Lock()

    print("\n" * len(args.group))  # Reserve space upfront

    for i, group in enumerate(args.group):
        try:
            parsed = ast.literal_eval(group)
            port = parsed[0]
            motor_ids = list(map(int, parsed[1:]))
            t = threading.Thread(target=monitor_group, args=(port, motor_ids, i, print_lock), daemon=True)
            threads.append(t)
            t.start()
        except Exception as e:
            print(f"Failed to parse group '{group}': {e}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all motor readers.")


if __name__ == "__main__":
    main()
