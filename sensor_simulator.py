import json
import random
import time
from datetime import datetime, timezone

from azure.iot.device import IoTHubDeviceClient, Message


def load_config(path: str = "config.json") -> dict:
    """
    Load configuration from config.json.
    Exits the program if the file cannot be loaded.
    """
    try:
        with open(path, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"[ERROR] Config file '{path}' not found. Make sure it is in the same folder as this script.")
        raise
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse '{path}': {e}")
        raise


def create_clients(devices_config):
    """
    For each device in the config, create an IoTHubDeviceClient.
    Returns a list of dictionaries with client and metadata.
    """
    clients = []
    for device in devices_config:
        cs = device["connectionString"]
        device_id = device["deviceId"]
        location_name = device["locationName"]

        print(f"[INFO] Creating client for device '{device_id}' at location '{location_name}'")
        client = IoTHubDeviceClient.create_from_connection_string(cs)

        clients.append(
            {
                "deviceId": device_id,
                "locationName": location_name,
                "client": client
            }
        )
    return clients


def generate_sensor_reading(location_name: str) -> dict:
    """
    Generate a single sensor reading for the given location.
    You can adjust ranges to be more realistic.
    """
    # Random but somewhat realistic ranges (tweak as you like)
    ice_thickness_cm = round(random.uniform(5.0, 45.0), 1)        # 5 to 45 cm
    surface_temp_c = round(random.uniform(-20.0, 2.0), 1)         # -20 to +2 C
    snow_accumulation_cm = round(random.uniform(0.0, 10.0), 1)    # 0 to 10 cm
    external_temp_c = round(random.uniform(-25.0, 5.0), 1)        # -25 to +5 C

    # Current timestamp in ISO 8601 UTC format
    timestamp_utc = datetime.now(timezone.utc).isoformat()

    payload = {
        "location": location_name,
        "iceThicknessCm": ice_thickness_cm,
        "surfaceTempC": surface_temp_c,
        "snowAccumulationCm": snow_accumulation_cm,
        "externalTempC": external_temp_c,
        "timestamp": timestamp_utc
    }

    return payload


def send_telemetry_loop(clients, interval_seconds: int):
    """
    Infinite loop that sends telemetry for each device every interval_seconds.
    Press Ctrl+C to stop.
    """
    print(f"[INFO] Starting telemetry loop. Sending every {interval_seconds} seconds.")
    print("[INFO] Press Ctrl+C to stop.\n")

    try:
        while True:
            for entry in clients:
                location_name = entry["locationName"]
                device_id = entry["deviceId"]
                client = entry["client"]

                reading = generate_sensor_reading(location_name)
                message_json = json.dumps(reading)
                message = Message(message_json)

                # Optional: set custom properties for routing or debugging
                message.content_encoding = "utf-8"
                message.content_type = "application/json"

                print(f"[SEND] Device: {device_id:<12} | Location: {location_name:<12} | "
                      f"Ice: {reading['iceThicknessCm']:>4} cm | "
                      f"SurfTemp: {reading['surfaceTempC']:>5} C | "
                      f"Snow: {reading['snowAccumulationCm']:>4} cm | "
                      f"ExtTemp: {reading['externalTempC']:>5} C | "
                      f"Time: {reading['timestamp']}")

                try:
                    client.send_message(message)
                except Exception as e:
                    print(f"[ERROR] Failed to send message from device '{device_id}': {e}")

            # Wait for the defined interval before sending again
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n[INFO] Telemetry loop stopped by user.")
    finally:
        print("[INFO] Closing IoT Hub clients...")
        for entry in clients:
            try:
                entry["client"].shutdown()
            except Exception:
                pass
        print("[INFO] All clients closed. Goodbye.")


def main():
    # 1. Load configuration
    config = load_config("config.json")

    # 2. Create IoT Hub clients
    devices_config = config.get("devices", [])
    if not devices_config:
        print("[ERROR] No devices found in config.json under 'devices' key.")
        return

    interval_seconds = int(config.get("sendIntervalSeconds", 10))

    clients = create_clients(devices_config)

    # 3. Start sending messages every interval_seconds
    send_telemetry_loop(clients, interval_seconds)


if __name__ == "__main__":
    main()
