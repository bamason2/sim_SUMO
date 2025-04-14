"""sensitivity study to determine sensitivity of inputs and their interactions to PM2.5 using 
sobol sensitivity analysis"""


import csv
import subprocess
import sys
import numpy as np


sys.path.append('/Users/byronmason/Code/sim_SUMO/tools')  #path to the tools directory
from experimental_design import sobol_sensitivity
from random_route import generate_route_file_defined_routes
from sumo_interface import run_sumo_simulation, parse_emission_data


TOTAL_VEHICLES = 1000
CONFIG_FILE = "./complex_juntion.sumocfg"
NET_FILE = "./complex_juntion.net.xml"
ROUTE_FILE = "./complex_juntion.rou.xml"
# TRIP_FILE = "./complex_juntion.trips.xml"
SIMULATION_DURATION = 3600
RESULTS_FILE = "./sensitivity_results.csv"
EMISSION_FILE = "./emissions_data.xml"
# EDGES = ["L7", "L8"]  # should be defined if required


# Possible routes for each vehicle type (these are specific to the network)

VEHICLE_ROUTES = {
   "pkw": {
      "L13": ['L40'],
      "L14": ['L41'],
      "L2": ['L10', 'L3', 'L4', 'L7', 'L9'],
      "L22": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L26": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L27": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L5": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L8": ['L1', 'L10', 'L3', 'L4', 'L9']    
   },
   "bus": {
      "L13": ['L40'],
      "L14": ['L41'],
      "L2": ['L10', 'L3', 'L4', 'L7', 'L9'],
      "L22": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L26": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L27": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L5": ['L1', 'L10', 'L3', 'L4', 'L7', 'L9'],
      "L8": ['L1','L10','L3','L4','L9']
   },
   "scooter": {
      "L2": ['L3', 'L7', 'L9'],
      "L22": ['L1','L3','L7', 'L9'],
      "L26": ['L1','L3','L7','L9'],
      "L5": ['L1','L3','L4','L7','L9'],
      "L8": ['L1','L3','L9']
   },
   "bike": {
      "L2": ['L3', 'L7', 'L9'],
      "L22": ['L1','L3','L7', 'L9'],
      "L26": ['L1','L3','L7','L9'],
      "L5": ['L1','L3','L4','L7','L9'],
      "L8": ['L1','L3','L9']
   }
}

# def get_random_route(vehicle_type, vehicle_routes):
#    """Randomly selects a source and sink route for a given vehicle type."""
#    if vehicle_type not in vehicle_routes:
#       raise ValueError(f"Vehicle type {vehicle_type} not found in vehicle routes.")
   
#    sources = list(vehicle_routes[vehicle_type].keys())
#    source = random.choice(sources)
#    sinks = vehicle_routes[vehicle_type][source]
#    sink = random.choice(sinks)
   
#    return source, sink

# generate the vehicle proportions for the sensitivity study
vehicle_counts = sobol_sensitivity(total_vehicles=TOTAL_VEHICLES)

# simulation loop
for index, vehicle_proportions in enumerate(vehicle_counts):

    # generate and write output_file for random routes according to the network
    # including ALL edges
    # generate_trip_file(
    #     net_file=NET_FILE,
    #     route_file=ROUTE_FILE,
    #     total_vehicles=TOTAL_VEHICLES,
    #     duration=SIMULATION_DURATION,
    #     vehicle_proportions=vehicle_proportions)

    # generate trip file using random sink to source routing *based on possible vehicle routes*
    generate_route_file_defined_routes(
        route_file=ROUTE_FILE,
        total_vehicles=TOTAL_VEHICLES,
        duration=SIMULATION_DURATION,
        vehicle_proportions=vehicle_proportions,
        vehicle_routes=VEHICLE_ROUTES)
    
   # generate trip file using random sink to source routing
   #  generate_route_file_sink_to_source(
   #      net_file=NET_FILE,
   #      route_file=ROUTE_FILE,
   #      total_vehicles=TOTAL_VEHICLES,
   #      duration=SIMULATION_DURATION,
   #      vehicle_proportions=vehicle_proportions)

    # generate route file from trip file
    command = [
        'duarouter',
        '--verbose', 'true',
         '--net-file',  NET_FILE, 
         '--trip-files', ROUTE_FILE, 
         '--output-file', ROUTE_FILE]

    subprocess.run(command, check=True)

    # run simulation
    print("Running simulation; ", index)
    run_sumo_simulation(config_file=CONFIG_FILE)

    # parse emissions
    emissions = parse_emission_data(emission_file=EMISSION_FILE)

    # save results
    # header = ['pkw', 'bus', 'scooter', 'bike', 'Total CO2 (mg)', 
    # 'Total CO mg)', 'Total HC (mg)', 'Total NOx (mg)', 'Total PMx (mg)', 'Total Fuel (mg)']
    combined = np.concatenate((vehicle_proportions, + emissions.values[0]))

    with open(RESULTS_FILE, mode='a', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(combined)
