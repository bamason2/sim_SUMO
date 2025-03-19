import xml.etree.ElementTree as ET
import os
import subprocess
import pandas as pd
import time


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

    # print("\n🚗 Vehicle Distribution for Current Scenario:")
    # for vtype, count in new_counts.items():
    #     print(f"  {vtype}: {count} vehicles ({new_percentages[vtype]}%)")

    for flow in root.findall("flow"):
        vtype = flow.get("type")
        if vtype in new_counts:
            original_count = int(flow.get("number"))
            type_ratio = original_count / vehicle_counts[vtype] if vehicle_counts[vtype] > 0 else 1
            flow.set("number", str(max(1, int(new_counts[vtype] * type_ratio))))

    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    # print(f"✅ Modified .rou.xml file saved as: {output_file}")

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
    # print(f"✅ Modified .sumocfg file saved as: {output_file}")

def run_sumo_simulation(config_file):
    """Runs SUMO simulation with the modified configuration file."""
    print("🚦 Running SUMO Simulation...")
    sumo_command = ["sumo", "-c", config_file]  # Use "sumo-gui" for GUI mode
    subprocess.run(sumo_command)

def parse_emission_data(emission_file):
    """Parses SUMO emission file and extracts vehicle emissions data."""
    if not os.path.exists(emission_file):
        print(f"❌ No emission data found for {emission_file}. Skipping...")
        return None

    tree = ET.parse(emission_file)
    root = tree.getroot()


    # Initialize total sums
    total_emissions = {
        "Total CO2 (g)": 0,
        "Total CO (g)": 0,
        "Total HC (g)": 0,
        "Total NOx (g)": 0,
        "Total PMx (g)": 0,
        "Total Fuel (L)": 0
    }

    # Extract and sum emissions
    for timestep in root.findall("timestep"):
        for vehicle in timestep.findall("vehicle"):
            total_emissions["Total CO2 (g)"] += float(vehicle.get("CO2", 0))
            total_emissions["Total CO (g)"] += float(vehicle.get("CO", 0))
            total_emissions["Total HC (g)"] += float(vehicle.get("HC", 0))
            total_emissions["Total NOx (g)"] += float(vehicle.get("NOx", 0))
            total_emissions["Total PMx (g)"] += float(vehicle.get("PMx", 0))
            total_emissions["Total Fuel (L)"] += float(vehicle.get("fuel", 0))

    # Convert to DataFrame
    df = pd.DataFrame([total_emissions])


    return df



# -------------------
# The following code coordinates calling of the functions above


# Original files
route_file = "simpleT.rou.xml"
config_file = "simpleT.sumocfg"
emission_file = "emissions_data.xml"


# Files to modify -> we dont need to safe modified files
modified_route_file = 'simpleT_scenario_modified.rou.xml'
modified_config_file = 'simpleT_scenario_modified.sumocfg'


# For a single simulation run
# ------------------------------

# New vehicle distribution
new_distribution = {"pkw": 0, "bus": 25, "bike": 15, "scooter": 10}

# Modify the files
adjust_vehicle_numbers(route_file, modified_route_file, new_distribution)
update_sumo_config(config_file, modified_config_file, modified_route_file, emission_file)

run_sumo_simulation(modified_config_file)

data = parse_emission_data(emission_file)
print(data)


# For multiple simulations run one after the other

# List of new vehicle distributions for multiple simulations
distributions = [
    {"pkw": 0, "bus": 100, "bike": 0, "scooter": 0},
    {"pkw": 100, "bus": 0, "bike": 0, "scooter": 0},
    {"pkw": 0, "bus": 0, "bike": 0, "scooter": 100}
]

# Iterate over each distribution and run the simulation
all_data = []

for i, new_distribution in enumerate(distributions):
    # Modify the files
    adjust_vehicle_numbers(route_file, modified_route_file, new_distribution)
    update_sumo_config(config_file, modified_config_file, modified_route_file, emission_file)

    run_sumo_simulation(modified_config_file)

    data = parse_emission_data(emission_file)
    if data is not None:
        all_data.append(data)

# Concatenate all data and print the final result
final_data = pd.concat(all_data, ignore_index=True)
print(final_data)