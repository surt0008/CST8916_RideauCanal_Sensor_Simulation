import json
import time
import random
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message

SEND_INTERVAL = 10  # seconds

DEVICES = [
    {
        "deviceId": "dows-lake",
        "location": "Dows Lake",
        "connectionString": "HostName=iot-rideau-canal-surt0008.azure-devices.net;DeviceId=dows-lake;SharedAccessKey=8aVIWbwBZw6nxY1Vy5ZGFv3kXmARmaeu5Ko6SPOAHuQ="
    },
    {
        "deviceId": "fifth-avenue",
        "location": "Fifth Avenue",
        "connectionString": "HostName=iot-rideau-canal-surt0008.azure-devices.net;DeviceId=fifth-avenue;SharedAccessKey=N6Jfn9l5PVpKR/I9KQ7dzp2Hma7void/LfDgRy4Ran0="
    },
    {
        "deviceId": "nac",
        "location": "NAC",
        "connectionString": "HostName=iot-rideau-canal-surt0008.azure-devices.net;DeviceId=nac;SharedAccessKey=rS6QxrycHEo793Ow8uK0mUZ9cIgpesY1wxMTXwN9Iqw="
    }
]


def generate_sensor_data(location):
    return {
        "location": location,
        "timestamp": datetime.utcnow().isoformat(),
        "iceThicknessCm": round(random.uniform(15, 40), 2),
        "surfaceTempC": round(random.uniform(-20, 5), 2),
        "snowAccumulationCm": round(random.uniform(0, 10), 2),
        "externalTempC": round(random.uniform(-25, 5), 2)
    }


def main():
    clients = []

    # Create IoT Hub clients
    for device in DEVICES:
        try:
            client = IoTHubDeviceClient.create_from_connection_string(
                device["connectionString"]
            )
            clients.append((client, device))
            print(f"[CONNECTED] {device['deviceId']}")
        except Exception as e:
            print(f"[ERROR] Could not connect device {device['deviceId']}: {e}")

    print("\n✅ Sensor simulation started...\n")

    while True:
        for client, device in clients:
            try:
                data = generate_sensor_data(device["location"])
                message = Message(json.dumps(data))
                message.content_type = "application/json"
                message.content_encoding = "utf-8"

                client.send_message(message)

                print(
                    f"[SENT] {device['deviceId']} | "
                    f"Ice: {data['iceThicknessCm']} cm | "
                    f"Temp: {data['surfaceTempC']} C | "
                    f"Snow: {data['snowAccumulationCm']} cm"
                )

            except Exception as e:
                print(f"[ERROR] Failed to send from {device['deviceId']}: {e}")

        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main()
