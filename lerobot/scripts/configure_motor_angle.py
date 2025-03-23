import argparse
import time


def configure_motor(port, brand, model, motor_idx_des, baudrate_des):
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

    motor_name = "motor"
    motor_index_arbitrary = motor_idx_des
    motor_model = model

    motor_bus = MotorsBusClass(port=port, motors={motor_name: (motor_index_arbitrary, motor_model)})

    try:
        motor_bus.connect()
        print(f"Connected on port {motor_bus.port}")
    except OSError as e:
        print(f"Error occurred when connecting to the motor bus: {e}")
        return

    try:
        print("Scanning all baudrates and motor indices")
        all_baudrates = set(SERIES_BAUDRATE_TABLE.values())
        motor_index = -1

        for baudrate in all_baudrates:
            motor_bus.set_bus_baudrate(baudrate)
            present_ids = motor_bus.find_motor_indices(list(range(1, 10)))
            if len(present_ids) > 1:
                raise ValueError("More than one motor ID detected. Disconnect all but one motor.")

            if len(present_ids) == 1:
                if motor_index != -1:
                    raise ValueError("More than one motor ID detected. Disconnect all but one motor.")
                motor_index = present_ids[0]
                break

        if motor_index == -1:
            raise ValueError("No motors detected. Ensure you have one motor connected.")

        print(f"Motor index found at: {motor_index}")

        if brand == "feetech":
            motor_bus.write_with_motor_ids(motor_bus.motor_models, motor_index, "Lock", 0)

        if baudrate != baudrate_des:
            print(f"Setting baudrate to {baudrate_des}")
            baudrate_idx = list(SERIES_BAUDRATE_TABLE.values()).index(baudrate_des)
            motor_bus.write_with_motor_ids(motor_bus.motor_models, motor_index, "Baud_Rate", baudrate_idx)
            time.sleep(0.5)
            motor_bus.set_bus_baudrate(baudrate_des)

        print(f"Setting motor ID to {motor_idx_des}")
        motor_bus.write_with_motor_ids(motor_bus.motor_models, motor_index, "ID", motor_idx_des)

        if brand == "feetech":
            motor_bus.write("Lock", 0)
            motor_bus.write("Maximum_Acceleration", 254)

        print("Starting to list motor angles continuously. Press Ctrl+C to stop.")
        while True:
            position = motor_bus.read("Present_Position")
            print(f"Motor Position: {position}")
            time.sleep(0.5)  # Adjust the frequency of position updates
    
    except KeyboardInterrupt:
        print("Stopping continuous angle listing.")
    except Exception as e:
        print(f"Error occurred during motor configuration: {e}")
    finally:
        motor_bus.disconnect()
        print("Disconnected from motor bus.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=str, required=True, help="Motors bus port")
    parser.add_argument("--brand", type=str, required=True, help="Motor brand (e.g. dynamixel, feetech)")
    parser.add_argument("--model", type=str, required=True, help="Motor model (e.g. xl330-m077, sts3215)")
    parser.add_argument("--ID", type=int, required=True, help="Desired motor ID")
    parser.add_argument("--baudrate", type=int, default=1000000, help="Desired baudrate for the motor")
    args = parser.parse_args()

    configure_motor(args.port, args.brand, args.model, args.ID, args.baudrate)