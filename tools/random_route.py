import random
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import sumolib

def get_edges_from_net(net_file):  #this needs to be changed to work with selected edges to better represent traffic across a junction
    """find edges for a given route .net file"""
    tree = ET.parse(net_file)
    root = tree.getroot()
    edges = []
    for edge in root.findall("edge"):
        edge_id = edge.get("id")
        if not edge_id.startswith(":"):  # skip internal junctions
            edges.append(edge_id)
    return edges

def weighted_choice(vehicle_proportions):
    """choose vehicle type based on random weights defined"""
    items = ['pkw', 'bus', 'scooter', 'bike']   # caution this is hard coded!!
    weights = vehicle_proportions/sum(vehicle_proportions)
    return random.choices(items, weights=weights, k=1)[0]

def generate_trips_defined(num_vehicles, duration, proportions, routes):
    """generate trips based on defined routes"""
    trips = []
    for i in range(num_vehicles):
        depart = round(random.uniform(0, duration), 2)  #depart time
        veh_type = weighted_choice(proportions)
        compatible_routes = routes.get(veh_type, [])
        if not compatible_routes:
            raise ValueError(f"No compatible routes found for vehicle type: {veh_type}")
        
        sources = list(routes[veh_type].keys())
        source = random.choice(sources)
        sinks = routes[veh_type][source]
        sink = random.choice(sinks)

        trips.append({
            "id": f"{veh_type}_{i}",
            "type": veh_type,
            "depart": depart,
            "from": source,
            "to": sink
        })
    return trips

def generate_trips(num_vehicles, duration, proportions, *args):
    """generate trips each trip is generated from a randomly chosen vehicle."""
    trips = []

    if len(args) == 2:
        for i in range(num_vehicles):
            depart = round(random.uniform(0, duration), 2)  #depart time
            veh_type = weighted_choice(proportions)
            from_edge = random.sample(args[1], 1)[0] # from source
            to_edge = random.sample(args[0], 1)[0] # to sink
            trips.append({
                "id": f"{veh_type}_{i}",
                "type": veh_type,
                "depart": depart,
                "from": from_edge,
                "to": to_edge
            })

    if len(args) == 1:
        for i in range(num_vehicles):
            depart = round(random.uniform(0, duration), 2)
            veh_type = weighted_choice(proportions)
            from_edge, to_edge = random.sample(args[0], 2)[0]
            trips.append({
                "id": f"{veh_type}_{i}",
                "type": veh_type,
                "depart": depart,
                "from": from_edge,
                "to": to_edge
            })
    return trips

def write_rou_file(filename, trips):
    """Write trips to a .rou.xml file with vehicle type definitions."""
    root = ET.Element("routes")

    # Define vehicle types
    vehicle_types = {
        "pkw": {"id": "pkw", "accel": "2.6", "decel": "4.5", "sigma": "0.5", "length": "4.5", "maxSpeed": "50"},
        "bus": {"id": "bus", "accel": "1.0", "decel": "3.0", "sigma": "0.5", "length": "12.0", "maxSpeed": "25"},
        "scooter": {"id": "scooter", "accel": "3.0", "decel": "4.5", "sigma": "0.5", "length": "2.0", "maxSpeed": "40"},
        "bike": {"id": "bike", "accel": "2.0", "decel": "4.0", "sigma": "0.5", "length": "1.8", "maxSpeed": "15"}
    }

    for vtype in vehicle_types.values():
        ET.SubElement(root, "vType", **vtype)

    # Add trips
    for trip in trips:
        ET.SubElement(root, "trip", attrib={
            "id": trip["id"],
            "type": trip["type"],
            "depart": str(trip["depart"]),
            "from": trip["from"],
            "to": trip["to"]})

    # Write to file
    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Generated {len(trips)} trips and saved to {filename}")

def plot_departure_histogram_by_type(trips, duration, num_bins=60):
    """plot the distribution of vehicle departures over normalised time by vehicle type"""
    type_to_departs = {}
    for trip in trips:
        vtype = trip["type"]
        norm_depart = trip["depart"] / duration
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

def generate_trip_file(net_file, route_file, total_vehicles, duration, vehicle_proportions):
    """generate random routes for a given vehicle proportions and write to a .rou.xml file"""
    edges = get_edges_from_net(net_file)
    trips = generate_trips(total_vehicles, duration, vehicle_proportions, edges)
    trips.sort(key=lambda x: x["depart"])
    write_rou_file(route_file, trips)


def get_sinks_and_sources(net_file):
    """get the sinks and sources from a .net.xml file"""

    # get sink and source edges
    net = sumolib.net.readNet(net_file)  # Load the network file

    sources = []  # Edges that only feed into the network
    sinks = []    # Edges that only allow exit

    for edge in net.getEdges():
        if len(edge.getIncoming()) == 0 and len(edge.getOutgoing()) > 0:
            sources.append(edge.getID())  # No incoming, only outgoing (entry edges)
        if len(edge.getOutgoing()) == 0 and len(edge.getIncoming()) > 0:
            sinks.append(edge.getID())  # No outgoing, only incoming (exit edges)

    return sinks, sources

def generate_route_file_defined_routes(
        route_file,
        total_vehicles,
        duration,
        vehicle_proportions,
        vehicle_routes):
    """generate random routes for a given vehicle proportions and write to a .rou.xml file"""

    trips = generate_trips_defined(
        total_vehicles,
        duration,
        vehicle_proportions,
        vehicle_routes)
    trips.sort(key=lambda x: x["depart"])
    write_rou_file(route_file, trips)

def generate_route_file_sink_to_source(
        net_file,
        route_file,
        total_vehicles,
        duration,
        vehicle_proportions):
    """generate random routes for a given vehicle proportions and write to a .rou.xml file"""

    # get sink and source edges
    sinks, sources = get_sinks_and_sources(net_file)
    if not sinks or not sources:
        raise ValueError("No sink or source edges found in the network file.")

    trips = generate_trips(
        total_vehicles,
        duration,
        vehicle_proportions,
        sinks,
        sources)
    trips.sort(key=lambda x: x["depart"])
    write_rou_file(route_file, trips)

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
