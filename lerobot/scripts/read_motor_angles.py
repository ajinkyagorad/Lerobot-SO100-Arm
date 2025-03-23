#!/usr/bin/env python3
"""
Reads Feetech motor angles continuously from the specified port and motor IDs.

Usage:
    python read_angles.py --port /dev/tty_left_follower --motors 1 2 3 4 5 6 7

Arguments:
    --port     : Serial port to which the motor bus is connected (e.g., /dev/tty_left_follower)
    --motors   : List of motor IDs to monitor

Example:
    python read_angles.py --port /dev/tty_left_follower --motors 1 2 3
"""

import time
import argparse
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus

def main():
    parser = argparse.ArgumentParser(description="Read motor angles over Feetech bus.")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/tty_left_follower or COM12)")
    parser.add_argument("--motors", type=int, nargs="+", required=True, help="List of motor IDs (e.g., 1 2 3 4 5)")

    args = parser.parse_args()
    port = args.port
    motor_ids = args.motors
    MODEL = "sts3215"

    motor_names = [f"motor_{i}" for i in motor_ids]
    motors = {name: (idx, MODEL) for name, idx in zip(motor_names, motor_ids)}

    bus = FeetechMotorsBus(port=port, motors=motors)
    bus.connect()
    bus.set_bus_baudrate(1_000_000)

    try:
        while True:
            angles = bus.read("Present_Angle", motor_names)
            print("Motor Angles (degrees):", angles)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Stopped reading motor angles.")
    finally:
        bus.disconnect()

if __name__ == "__main__":
    main()
