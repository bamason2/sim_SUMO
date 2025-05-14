" results analysis and visualisation"


import os
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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

def display_table(df, title="", fontsize=12):
    """function to display a dataframe from sobol analysis as a formatted table"""
    _, ax = plt.subplots(figsize=(max(6, len(df.columns)*2), len(df)*0.6 + 1))
    ax.axis('off')
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center',
        cellLoc='center',
        colLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    table.scale(1.2, 1.2)
    ax.set_title(title, fontweight='bold', fontsize=fontsize + 2)
    plt.show()

def plot_departure_histogram_by_type(veh_data, duration, num_bins=60):
    """plot the distribution of vehicle departures over normalised time by vehicle type"""
    type_to_departs = {}
    for vehicle in veh_data:
        vtype = vehicle["type"]
        norm_depart = float(vehicle["depart"]) / duration
        type_to_departs.setdefault(vtype, []).append(norm_depart)
    bins = np.linspace(0, 1, num_bins + 1)
    bin_width = bins[1] - bins[0]
    bin_centers = bins[:-1] + bin_width / 2
    type_histograms = {}
    for vtype, times in type_to_departs.items():
        hist, _ = np.histogram(times, bins=bins)
        type_histograms[vtype] = hist
    vehicle_types_sorted = sorted(type_histograms.keys())
    colors = {"pkw": "#1f77b4", "bus": "#ff7f0e", "scooter": "#2ca02c", "bike": "#d62728"}
    bottom = np.zeros(len(bin_centers))
    plt.figure(figsize=(10, 4))
    for vtype in vehicle_types_sorted:
        counts = type_histograms[vtype]
        plt.bar(bin_centers, counts, width=bin_width, bottom=bottom,
                label=vtype, color=colors.get(vtype, None), edgecolor='black')
        bottom += counts
    plt.xlabel("Normalized Simulation Time (0–1)")
    plt.ylabel("Number of Vehicles")
    plt.title("Vehicle Departures Over Time (Histogram by Type)")
    plt.legend(title="Vehicle Type")
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

def plot_departure_histogram(vehicle_info, duration, num_bins=60):
    """plot the distribution of vehicle departures over normalised time by vehicle type"""

    type_to_departs = {}
    for vehicle in vehicle_info:
        vtype = vehicle["type"]
        norm_depart = vehicle["depart"] / duration
        type_to_departs.setdefault(vtype, []).append(norm_depart)

    bins = np.linspace(0, 1, num_bins + 1)
    bin_width = bins[1] - bins[0]
    bin_centers = bins[:-1] + bin_width / 2
    type_histograms = {}
    for vtype, times in type_to_departs.items():
        hist, _ = np.histogram(times, bins=bins)
        type_histograms[vtype] = hist
    vehicle_types_sorted = sorted(type_histograms.keys())
    colors = {"pkw": "#1f77b4", "bus": "#ff7f0e", "scooter": "#2ca02c", "bike": "#d62728"}
    bottom = np.zeros(len(bin_centers))
    plt.figure(figsize=(10, 4))
    for vtype in vehicle_types_sorted:
        counts = type_histograms[vtype]
        plt.bar(bin_centers, counts, width=bin_width, bottom=bottom,
                label=vtype, color=colors.get(vtype, None), edgecolor='black')
        bottom += counts
    plt.xlabel("Normalized Simulation Time (0–1)")
    plt.ylabel("Number of Vehicles")
    plt.title("Vehicle Departures Over Time (Histogram by Type)")
    plt.legend(title="Vehicle Type")
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

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

def get_vehicle_info(route_file):
    """get the start times for each vehicle in the simulation from data.xml"""
    tree = ET.parse(route_file)
    root = tree.getroot()

    vehicle_info=[]
    for vehicle in root.findall("vehicle"):
        vehicle_id = vehicle.get("id")
        vehicle_type = vehicle.get("type")
        depart_time = vehicle.get("depart")
        vehicle_info.append({
            "ID": vehicle_id, 
            "type": vehicle_type, 
            "depart": depart_time})

    # Convert to DataFrame
    # df = pd.DataFrame(vehicle_info)

    return vehicle_info


def get_trips_from_rou(route_file):
    """parse trips from a .rou.xml file and return as a list of dicts"""
    tree = ET.parse(route_file)
    root = tree.getroot()
    trips = []
    for trip in root.findall("trip"):
        trips.append({
            "id": trip.get("id"),
            "type": trip.get("type"),
            "depart": float(trip.get("depart")),
            "from": trip.get("from"),
            "to": trip.get("to")
        })
    return trips
