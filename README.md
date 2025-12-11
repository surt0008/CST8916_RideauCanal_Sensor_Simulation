#  Rideau Canal Sensor Simulation  
**CST8916 – Remote Data and RT Applications**  
Sensor Simulator for IoT Data Pipeline  

---

# Overview

The Rideau Canal Sensor Simulation project generates realistic ice-monitoring sensor data and sends it to Azure IoT Hub.  
This data represents multiple Rideau Canal locations and includes:

- Ice thickness  
- Surface temperature  
- Snow accumulation  
- External temperature  
- Location  
- Timestamps  

The simulator continuously sends readings just like physical IoT sensors would.  
These readings are later used for:

- Stream Analytics processing  
- Cosmos DB storage  
- Blob Storage archiving  
- Dashboard visualization  

---

#  Technologies Used

| Technology                        | Purpose                               |
|----------------------------------|----------------------------------------|
| Python 3.x                       | Main scripting language                |
| Azure IoT Device SDK for Python | Sending telemetry to Azure IoT Hub     |
| Azure IoT Hub                    | Cloud entry point for sensor data      |
| dotenv (.env)                   | Secure configuration storage           |
| JSON                             | Data formatting                        |

---

#  Prerequisites

Before running the simulator, ensure you have:

### ✔ Python 3.8+ installed  
Check using:  
```bash
python --version
```

### ✔ Azure Resources created  
Your Azure resource group must already include:
- IoT Hub (iot-rideau-canal-surt0008)
- Devices:
    - dows-lake
    - fifth-avenue
    - nac
- Stream Analytics Job (connected to IoT Hub input)
- Cosmos DB + container (SensorAggregations)
- Blob Storage container (historical-data)

### ✔ Required Python libraries installed  
Install with:  
```bash
pip install azure-iot-device python-dotenv
```

### ✔ A `.env` file at the project root  
Containing:  
```bash
IOTHUB_DEVICE_CONNECTION_STRING=your_device_connection_string_here
SEND_INTERVAL_SECONDS=5
```

---

#  Installation

Clone the repository:
```bash
git clone https://github.com/surt0008/CST8916_RideauCanal_Sensor_Simulation.git

cd CST8916_RideauCanal_Sensor_Simulation
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create your `.env` file: 

Add:
```bash
IOTHUB_DEVICE_CONNECTION_STRING=your_connection_string_here
SEND_INTERVAL_SECONDS=5
```

---

#  Usage

Start the simulator using:
```bash
python sensor_simulator.py
```

You will see output like:
```bash
Sending message: {"location":"DowsLake", "iceThickness": 23.4, ... }
Message successfully sent!
```

Telemetry is sent every `SEND_INTERVAL_SECONDS` seconds (default: 5 seconds).

To stop the simulator:
CTRL + C

---
#  How the Code Works

## **1. Device Setup**

All IoT devices are listed with:

- `deviceId`
- `location`
- `connectionString`

Each device gets its own `IoTHubDeviceClient`.

---

## **2. Sensor Data Generation**

Function:
```bash
def generate_sensor_data(location):
```

This creates realistic values:

- `iceThicknessCm`: 15–40 cm  
- `surfaceTempC`: –20 to +5 °C  
- `snowAccumulationCm`: 0–10 cm  
- `externalTempC`: –25 to +5 °C  

Plus ISO timestamp:
```bash
"timestamp": datetime.utcnow().isoformat()
```

---

## **3. Sending Data**

Every **10 seconds**:

- Data is converted to JSON  
- Sent as a `Message` to Azure IoT Hub  

Data pipeline:
```bash
Azure IoT Hub → Stream Analytics → Cosmos DB / Blob Storage
```

---

#  Main Components Explained

### **sensor_simulator.py**
Handles:

- Loading IoT Hub connection string  
- Generating sensor values  
- Sending telemetry using Azure IoT device client  
- Printing logs and handling reconnect attempts   

---

#  Sensor Data Format

Every message is sent in JSON format.

###  JSON Schema

```bash
{
"location": "string",
"iceThickness": "number",
"surfaceTemperature": "number",
"snowAccumulation": "number",
"externalTemperature": "number",
"timestamp": "ISO 8601 datetime"
}
```

---

###  Example Output
```bash
{
"location": "DowsLake",
"iceThickness": 22.5,
"surfaceTemperature": -5.2,
"snowAccumulation": 3.4,
"externalTemperature": -11.0,
"timestamp": "2025-12-11T03:41:22Z"
}
```


---

#  Troubleshooting

### 1. Dashboard Stuck on “Loading…”
Symptom:
- Cosmos DB had documents
- Dashboard stayed on loading
- Status only showed “Safe”

Cause:
- Location names stored by simulation (“Dows Lake”)
didn’t match dashboard expected names (“Dow's Lake”)
- Result: queries returned zero documents

Fix:
- Added location mapping in server.js
- Normalized DB & UI names
- Dashboard immediately showed correct data

### 2. Stream Analytics Error – RequiredColumnMissing
Error seen:

OutputDataConversionError.RequiredColumnMissing
Cause:
- The Stream Analytics query output fields didn’t match the Cosmos DB container schema.
- Specifically, Cosmos required fields like location, windowEndTime, or metrics that were missing.

Fix:
- Updated the Stream Analytics query
- Ensured fields exactly match Cosmos documents
- Recreated the output container if needed
- Restarted Stream Analytics

### 3. Stream Analytics Not Writing to Cosmos DB
Symptom:
- You could see data in Blob Storage
- But Cosmos DB showed nothing

Cause:
- Output alias mismatch (cosmosoutput vs. SensorAggregations)
- Wrong partition key
- Old documents causing schema mismatches

Fix:
- Dropped all old documents in the container
- Ensured container is created automatically with correct schema
- Verified output name EXACTLY matches "SensorAggregations"
- Re-ran analytics job

---


#  Conclusion

This simulator forms the first stage of your entire IoT pipeline.  
It reliably generates realistic data and sends it into the Azure environment, enabling:

- Real-time monitoring  
- Stream analytics aggregation  
- Dashboard visualizations  
- Historical storage  

It is simple, reliable, and accurately models the Rideau Canal ice conditions.

#  AI Tools Disclosure
I used ChatGPT only for help with wording in the documentation, general coding guidance, and small debugging tips. All the sensor simulator coding, Azure setup, testing, and actual implementation were done entirely by me.