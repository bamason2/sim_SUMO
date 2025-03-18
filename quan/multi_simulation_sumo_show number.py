import xml.etree.ElementTree as ET
import os
import subprocess
import pandas as pd
import time

# Define 5 Traffic Scenarios (Each must sum to 100%)
SIMULATIONS = [
    {"pkw": 100, "bus": 0, "bike": 0, "scooter": 0},  # Scenario 1
    {"pkw": 0, "bus": 25, "bike":50, "scooter": 25},  # Scenario 2
    {"pkw": 30, "bus": 20, "bike": 20, "scooter": 30},  # Scenario 3
    {"pkw": 0, "bus": 35, "bike": 30, "scooter": 20},  # Scenario 4
    {"pkw": 0, "bus": 0, "bike": 0, "scooter": 100}   # Scenario 5
]

# File paths
ROUTE_FILE = "simpleT.rou.xml"
CONFIG_FILE = "simpleT.sumocfg"
EMISSION_FILES = [
    "emissions_data_scenario1.xml",
    "emissions_data_scenario2.xml",
    "emissions_data_scenario3.xml",
    "emissions_data_scenario4.xml",
    "emissions_data_scenario5.xml"
]

def get_total_vehicles(root, vehicle_types):
    """Get the total number of each vehicle type in the file."""
    total_vehicles = 0
    vehicle_counts = {vtype: 0 for vtype in vehicle_types}
    
    for flow in root.findall("flow"):
        vtype = flow.get("type")
        if vtype in vehicle_counts:
            count = int(flow.get("number"))
            vehicle_counts[vtype] += count
            total_vehicles += count

    return total_vehicles, vehicle_counts

def adjust_vehicle_numbers(xml_file, output_file, new_percentages):
    """Adjust vehicle numbers in .rou.xml based on given percentages."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    vehicle_types = new_percentages.keys()
    total_vehicles, vehicle_counts = get_total_vehicles(root, vehicle_types)

    # Compute new counts based on percentages
    new_counts = {vtype: int((new_percentages[vtype] / 100) * total_vehicles) for vtype in vehicle_types}

    print("\n🚗 Vehicle Distribution for Current Scenario:")
    for vtype, count in new_counts.items():
        print(f"  {vtype}: {count} vehicles ({new_percentages[vtype]}%)")

    for flow in root.findall("flow"):
        vtype = flow.get("type")
        if vtype in new_counts:
            original_count = int(flow.get("number"))
            type_ratio = original_count / vehicle_counts[vtype] if vehicle_counts[vtype] > 0 else 1
            flow.set("number", str(max(1, int(new_counts[vtype] * type_ratio))))

    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Modified .rou.xml file saved as: {output_file}")

def update_sumo_config(config_file, output_file, new_route_file, emission_file):
    """Updates the SUMO configuration file to use the modified .rou.xml file and set emission output."""
    tree = ET.parse(config_file)
    root = tree.getroot()

    for elem in root.findall(".//route-files"):
        elem.set("value", new_route_file)

    # Update emission output file
    processing = root.find(".//processing")
    if processing is None:
        processing = ET.SubElement(root, "processing")
    
    emission_elem = processing.find(".//emission-output")
    if emission_elem is None:
        emission_elem = ET.SubElement(processing, "emission-output")
    
    emission_elem.set("value", emission_file)

    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Modified .sumocfg file saved as: {output_file}")

def run_sumo_simulation(config_file):
    """Runs SUMO simulation with the modified configuration file."""
    print("🚦 Running SUMO Simulation...")
    sumo_command = ["sumo", "-c", config_file]  # Use "sumo-gui" for GUI mode
    subprocess.run(sumo_command)

def parse_emission_data(emission_file, scenario):
    """Parses SUMO emission file and extracts vehicle emissions data."""
    if not os.path.exists(emission_file):
        print(f"❌ No emission data found for {emission_file}. Skipping...")
        return None

    tree = ET.parse(emission_file)
    root = tree.getroot()

    data = []
    for vehicle in root.findall("vehicle"):
        vehicle_id = vehicle.get("id")
        co2 = float(vehicle.get("CO2"))
        co = float(vehicle.get("CO"))
        pmx = float(vehicle.get("PMx"))
        nox = float(vehicle.get("NOx"))
        fuel = float(vehicle.get("fuel"))
        vehicle_class = vehicle.get("type")

        data.append([scenario, vehicle_id, vehicle_class, co2, co, pmx, nox, fuel])

    return pd.DataFrame(data, columns=["Scenario", "Vehicle ID", "Vehicle Type", "CO2", "CO", "PMx", "NOx", "Fuel"])

if __name__ == "__main__":
    all_emission_data = []

    for i, new_distribution in enumerate(SIMULATIONS, start=1):
        print(f"\n🔄 Running Simulation {i} with Distribution: {new_distribution}")

        # Modify files
        modified_route_file = f"modified_simpleT_scenario{i}.rou.xml"
        modified_config_file = f"modified_simpleT_scenario{i}.sumocfg"
        emission_file = EMISSION_FILES[i-1]

        adjust_vehicle_numbers(ROUTE_FILE, modified_route_file, new_distribution)
        update_sumo_config(CONFIG_FILE, modified_config_file, modified_route_file, emission_file)

        # Run SUMO Simulation
        run_sumo_simulation(modified_config_file)

        # Wait for emission data to be generated
        time.sleep(2)

        # Parse emission data
        df_emission = parse_emission_data(emission_file, scenario=i)
        if df_emission is not None:
            all_emission_data.append(df_emission)

    # Combine all emission data
    df_all = pd.concat(all_emission_data, ignore_index=True) if all_emission_data else pd.DataFrame()

    # Step 6: Print Final Emission Summary
    if not df_all.empty:
        emission_summary = df_all.groupby(["Scenario", "Vehicle Type"])[["CO2", "CO", "PMx", "NOx", "Fuel"]].mean().reset_index()
        print("\n📊 Average Emissions per Scenario & Vehicle Type:")
        print(emission_summary.to_string(index=False))
    else:
        print("❌ No emission data available for analysis.")
