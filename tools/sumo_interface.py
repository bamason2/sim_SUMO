"""Some functions to run sumo simulation and parse emission data"""

import subprocess
import os
import xml.etree.ElementTree as ET
import pandas as pd


def run_sumo_simulation(config_file):
    """Run SUMO simulation with the specified configuration file"""
    sumo_command = ["sumo", "-c", config_file]
    subprocess.run(sumo_command, check=False)

def parse_emission_data(emission_file):
    """Parse SUMO emission file and extracts vehicle emissions data"""

    if not os.path.exists(emission_file):
        print(f"No emission data found for {emission_file}. Skipping...")
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

def parse_trip_emissions(trip_file="data.xml"):
    """Parse SUMO trip file and extracts vehicle emissions"""

# sum total emissions for each vehicle type in trip_file
    tree = ET.parse(trip_file)
    root = tree.getroot()

# get PMx_abs for each tripinfo with vehicle type
    emissions = []
    for tripinfo in root.findall("tripinfo"):
        vehicle_type = tripinfo.get("vType")
        emissions_data = tripinfo.find("emissions")
        pmx_abs = float(emissions_data.get("PMx_abs", 0))
        emissions.append({"Vehicle Type": vehicle_type, "PMx_abs": pmx_abs})

    # Convert to DataFrame
    df = pd.DataFrame(emissions)

    # sum all values in PMx_abs
    total_Pm = float(df["PMx_abs"].sum())

    # Group by vehicle type and sum emissions
    # df_grouped = df.groupby("Vehicle Type").sum().reset_index()

    return total_Pm
