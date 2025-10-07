


"""
Trip writer with a single vType where we set 10 parameters from vtype_params.
All values are formatted to 1 decimal place when written to XML.
Defaults are midpoints of the provided ranges.
"""

"""
Trip writer with a single vType where we set 10 parameters from vtype_params.
All values are formatted to 1 decimal place when written to XML.
Defaults are midpoints of the provided ranges.
"""

from typing import Dict, List, Tuple, Optional
import random
import xml.etree.ElementTree as ET
import sumolib

def get_edges_from_net(net_file: str) -> List[str]:
    tree = ET.parse(net_file)
    root = tree.getroot()
    edges = []
    for edge in root.findall("edge"):
        eid = edge.get("id")
        if eid and not eid.startswith(":"):
            edges.append(eid)
    return edges

def get_sinks_and_sources(net_file: str) -> Tuple[List[str], List[str]]:
    net = sumolib.net.readNet(net_file)
    sources, sinks = [], []
    for e in net.getEdges():
        if len(e.getIncoming()) == 0 and len(e.getOutgoing()) > 0:
            sources.append(e.getID())
        if len(e.getOutgoing()) == 0 and len(e.getIncoming()) > 0:
            sinks.append(e.getID())
    return sinks, sources

def generate_trips_defined(num_vehicles: int, duration: float, routes: Dict[str, Dict[str, List[str]]],
                           seed: Optional[int] = None) -> List[dict]:
    if seed is not None:
        random.seed(seed)
    groups = list(routes.keys())
    if not groups:
        raise ValueError("routes is empty")
    trips = []
    for i in range(num_vehicles):
        depart = round(random.uniform(0, duration), 2)
        g = random.choice(groups)
        vmap = routes[g]
        src = random.choice(list(vmap.keys()))
        dst = random.choice(vmap[src])
        trips.append({"id": f"veh_{i}", "depart": depart, "from": src, "to": dst})
    return trips

def write_trip_file(trip_filename: str, trips: List[dict], vtype_params: Optional[dict] = None, vtype_id: str = "moped") -> None:
    """
    vtype_params should contain keys for the 10 parameters (names in experimental_design.NAMES).
    Values will be formatted to 1 decimal place.
    """
    vp = vtype_params.copy() if vtype_params else {}

    def g(key, default):
        v = vp.get(key, default)
        # format to one decimal if it's numeric, else keep as str
        try:
            return f"{float(v):.1f}"
        except Exception:
            return str(v)

    root = ET.Element("routes")

    # Midpoint defaults per table; formatted to 1 decimal automatically by g()
    vtype = {
        "id": vtype_id,
        # car-following
        "accel": g("acceleration", 7.0),              # [4,10]
        "decel": g("deceleration", 9.0),              # [6,12]
        "minGap": g("minGap", 1.4),                   # [0.3,2.5]
        "maxSpeed": "11.11",
        
        # lane-changing
        "lcSpeedGain": g("lcSpeedGain", 2.65),        # [0,5.3]
        "lcCooperative": g("lcCooperative", 0.5),     # [0,1]
        "lcPushy": g("lcPushy", 0.5),                 # [0,1]
        "lcStrategic": g("lcStrategic", 2.95),        # [0,5.9]
        "lcAssertive": g("lcAssertive", 1.25),        # [0,2.5]
  
        # misc
        "vClass": "motorcycle",
        "length": "2.0",
        "color": "0,255,0",
        "emissionClass": "HBEFA4/MC_4S_le250cc_Euro-3",
    }
    ET.SubElement(root, "vType", **vtype)

    for t in trips:
        ET.SubElement(root, "trip", attrib={
            "id": t["id"],
            "type": vtype_id,
            "depart": f"{float(t['depart']):.2f}",
            "from": t["from"],
            "to": t["to"],
        })

    ET.ElementTree(root).write(trip_filename, encoding="utf-8", xml_declaration=True)
    print(f"Generated {len(trips)} trips with vType '{vtype_id}' → {trip_filename}")

def generate_trip_file_defined_routes(trip_file: str, total_vehicles: int, duration: float,
                                      vehicle_routes: Dict[str, Dict[str, List[str]]],
                                      vtype_params: Optional[dict] = None, seed: Optional[int] = None) -> None:
    trips = generate_trips_defined(total_vehicles, duration, vehicle_routes, seed=seed)
    trips.sort(key=lambda x: x["depart"])
    write_trip_file(trip_file, trips, vtype_params=vtype_params)

