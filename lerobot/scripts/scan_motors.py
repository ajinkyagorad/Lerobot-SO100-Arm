import argparse

def scan_motors(port, brand, model):
    if brand == "feetech":
        from lerobot.common.robot_devices.motors.feetech import MODEL_BAUDRATE_TABLE
        from lerobot.common.robot_devices.motors.feetech import (
            SCS_SERIES_BAUDRATE_TABLE as SERIES_BAUDRATE_TABLE,
        )
        from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus as MotorsBusClass
    elif brand == "dynamixel":
        from lerobot.common.robot_devices.motors.dynamixel import MODEL_BAUDRATE_TABLE
        from lerobot.common.robot_devices.motors.dynamixel import (
            X_SERIES_BAUDRATE_TABLE as SERIES_BAUDRATE_TABLE,
        )
        from lerobot.common.robot_devices.motors.dynamixel import DynamixelMotorsBus as MotorsBusClass
    else:
        raise ValueError(
            f"Currently we do not support this motor brand: {brand}. We currently support feetech and dynamixel motors."
        )

    if model not in MODEL_BAUDRATE_TABLE:
        raise ValueError(
            f"Invalid model '{model}' for brand '{brand}'. Supported models: {list(MODEL_BAUDRATE_TABLE.keys())}"
        )

    motor_bus = MotorsBusClass(port=port, motors={})

    try:
        motor_bus.connect()
        print(f"Connected on port {motor_bus.port}")
    except OSError as e:
        print(f"Error occurred when connecting to the motor bus: {e}")
        return

    try:
        print("Scanning motor IDs from 1 to 6")
        found_motors = []

        for motor_id in range(1, 7):  # Check IDs from 1 to 6
            try:
                motor_bus.set_bus_baudrate(1000000)  # Set a common baudrate
                # Attempt to read the motor ID
                present_ids = motor_bus.find_motor_indices([motor_id])
                if present_ids:
                    found_motors.extend(present_ids)
                    print(f"Motor ID {motor_id} is present.")
                else:
                    print(f"Motor ID {motor_id} is not detected.")
            except Exception as e:
                print(f"Error checking motor ID {motor_id}: {e}")

        if not found_motors:
            print("No motors detected in the specified range. Ensure they are connected properly.")
        else:
            print(f"Total found motor IDs: {set(found_motors)}")  # Print unique motor IDs

    except Exception as e:
        print(f"Error occurred during motor scanning: {e}")
    finally:
        motor_bus.disconnect()
        print("Disconnected from motor bus.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, required=True, help="Motors bus port")
    parser.add_argument("--brand", type=str, required=True, help="Motor brand (e.g. dynamixel, feetech)")
    parser.add_argument("--model", type=str, required=True, help="Motor model (e.g. xl330-m077, sts3215)")
    args = parser.parse_args()

    scan_motors(args.port, args.brand, args.model)