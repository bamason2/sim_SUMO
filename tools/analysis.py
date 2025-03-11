import xml.etree.ElementTree as ET
import pandas as pd





def sumo_xml_to_csv(xml_file, csv_file):
    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract data
    data = []
    for timestep in root.findall("timestep"):
        time = float(timestep.get("time"))
        for vehicle in timestep.findall("vehicle"):
            vid = vehicle.get("id")
            co2 = float(vehicle.get("CO2", 0))
            co = float(vehicle.get("CO", 0))
            nox = float(vehicle.get("NOx", 0))
            pmx = float(vehicle.get("PMx", 0))
            fuel = float(vehicle.get("fuel", 0))
            speed = float(vehicle.get("speed", 0))
            
            data.append([time, vid, co2, co, nox, pmx, fuel, speed])

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=["Time", "Vehicle", "CO2 (g/s)", "CO (g/s)", "NOx (g/s)", "PMx (g/s)", "Fuel (L/s)", "Speed (m/s)"])

    # Save as CSV
    df.to_csv(csv_file, index=False)
    print(f"Converted {xml_file} to {csv_file}")

    return df

# Convert emissions.xml to emissions.csv
df = sumo_xml_to_csv("emissions_data.xml", "test.csv")

# Display CSV data in chat
# import ace_tools as tools
# tools.display_dataframe_to_user(name="SUMO Emissions CSV", dataframe=df)
