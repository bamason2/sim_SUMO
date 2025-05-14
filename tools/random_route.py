"generate random routes for SUMO simulation"
# This script generates random routes for a SUMO simulation based on vehicle 
# proportions and network data.

import random
import xml.etree.ElementTree as ET
import sumolib

def get_edges_from_net(net_file):  
    #this needs to be changed to work with selected edges
    # to better represent traffic across a junction
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

def write_trip_file(trip_filename, trips):
    """Create a .rou.xml file with vehicle type definitions from trips"""
    root = ET.Element("routes")

    # Define vehicle types
    vehicle_types = {
        "pkw": {
            "id": "pkw", 
            "accel": "2.6", 
            "decel": "4.5", 
            "sigma": "0.5", 
            "length": "4.5", 
            "maxSpeed": "11.11",
            "vClass": "passenger",
            "color" : "0,255,0",
            "emissionClass": "HBEFA4/PC_petrol_Euro-4"
            },
        "bus": {
            "id": "bus", 
            "accel": "1.0", 
            "decel": "3.0", 
            "sigma": "0.5", 
            "length": "12.0",  
            "color" : "128, 0, 128",  
            "maxSpeed": "11.11",
            "vClass" : "bus",
            "emissionClass": "HBEFA4/RT_gt14-20t_Euro-IV_EGR" 
            },
        "scooter": {
            "id": "scooter", 
            "accel": "3.0", 
            "decel": "4.5", 
            "sigma": "0.5", 
            "length": "2.0", 
            "color" : "255,0,0", 
            "maxSpeed": "11.11", 
            "vClass" : "moped", 
            "emissionClass" : "HBEFA4/MC_4S_le250cc_Euro-4"
            },
        "bike": {
            "id": "bike", 
            "accel": "2.0", 
            "decel": "4.0", 
            "sigma": "0.5", 
            "length": "1.8", 
            "maxSpeed": "4.17", 
            "color" : "0,0,255",
            "vClass" : "bicycle",
            "emissionClass" : "Zero"
            }
    }
##<!--update parameter for safety-->
#    <vType sigma="0.15" speedDev="0.15" minGap="2.5" vClass="passenger" color="0,255,0"/>
#    <vType  accel="1.0" decel="2.0" sigma="0.05" speedDev="0.1" minGap="3.0" vClass="bus"/>
#    <vType id="bike" length="1.8" width="0.5" maxSpeed="6.5" departSpeed="max" departLane="best" accel="0.7" decel="1.3" sigma="0.25" speedDev="0.4" minGap="0.6" minGapLat="0.4" vClass="bicycle"/>
#    <vType id="scooter" length="2" maxSpeed="45" departSpeed="max" departLane="best" accel="2.3" decel="4.0" sigma="0.3" speedDev="0.15" minGap="0.7" minGapLat="0.4" lcOvertakeRight="0.5" lcCooperative="0.3" lcAssertive="0.7" lcSpeedGain="0.5" tau="1.1" emissionClass="HBEFA4/MC_4S_le250cc_Euro-4" vClass="moped" color="255,0,0"/>

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
    tree.write(trip_filename, encoding="utf-8", xml_declaration=True)
    print(f"Generated {len(trips)} trips and saved to {trip_filename}")

def generate_trip_file(net_file, route_file, total_vehicles, duration, vehicle_proportions):
    """generate random routes for a given vehicle proportions and write to a .rou.xml file"""
    edges = get_edges_from_net(net_file)
    trips = generate_trips(total_vehicles, duration, vehicle_proportions, edges)
    trips.sort(key=lambda x: x["depart"])
    write_trip_file(route_file, trips)

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

def generate_trip_file_defined_routes(
        trip_file,
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
    
    write_trip_file(trip_file, trips)

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
    write_trip_file(route_file, trips)


