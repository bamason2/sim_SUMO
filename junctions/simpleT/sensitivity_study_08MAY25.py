"Sensitivity study for SUMO simulation with defined routes"
# This script generates vehicle proportions using Sobol 
# sensitivity analysis and runs a SUMO simulation for each set 
# of proportions.


import csv
import subprocess
import sys
import numpy as np

from tools.experimental_design import sobol_sensitivity
from tools.random_route import generate_route_file_defined_routes
from tools.sumo_interface import run_sumo_simulation, parse_trip_emissions

# Constants
TOTAL_VEHICLES = 1100

CONFIG_FILE = "simpleT.sumocfg"
NET_FILE = "simpleT.net.xml"
ROUTE_FILE = "simpleT.rou.xml"

SIMULATION_DURATION = 3600
RESULTS_FILE = "./simpleT_sensitivity_results_08MAY25.csv"
EMISSION_FILE = "./emissions_data.xml"
TRIP_DATA_FILE = "./data.xml"

# Vehicle routes, as per the network
VEHICLE_ROUTES = {
   "pkw": {
      "L14": ['L16', 'L18'],
      "L15": ['L13', 'L18'],
      "L17": ['L13', 'L16']
   },
   "bus": {
      "L14": ['L16', 'L18'],
      "L15": ['L13', 'L18'],
      "L17": ['L13', 'L16']
   },
   "scooter": {
      "L14": ['L16', 'L18'],
      "L15": ['L13', 'L18'],
      "L17": ['L13', 'L16']
   },
   "bike": {
      "L14": ['L16', 'L18'],
      "L15": ['L13', 'L18'],
      "L17": ['L13', 'L16']
   }
}

# Generate the vehicle proportions for the sensitivity study
vehicle_counts = sobol_sensitivity(total_vehicles=TOTAL_VEHICLES)

# If the results file already exists exit the script if not continue
try:
    with open(RESULTS_FILE, 'r', encoding="utf-8") as file:
        print(f"Results file {RESULTS_FILE} already exists. Exiting script.")
        sys.exit()
except FileNotFoundError:
    pass


# Simulation loop

for index, vehicle_proportions in enumerate(vehicle_counts):

    # Generate and write output file for random routes according to the network
    generate_route_file_defined_routes(
      route_file=ROUTE_FILE,
      total_vehicles=TOTAL_VEHICLES,
      duration=SIMULATION_DURATION,
      vehicle_proportions=vehicle_proportions,
      vehicle_routes=VEHICLE_ROUTES)
    
    # Generate route file from trip file
    command = [
      'duarouter',
      '--verbose', 'true',
      '--net-file', NET_FILE,
      '--route-files', ROUTE_FILE,
      '--output-file', ROUTE_FILE
   ]

    # Run duarouter to generate routes
    subprocess.run(command, check=True)

    # Run simulation
    print(f"Running simulation {index}...")
    run_sumo_simulation(config_file=CONFIG_FILE)

    # Parse emissions (using parse_emission_data)
   #  emissions = parse_emission_data(emission_file=EMISSION_FILE)

    # Save results
   #  combined = np.concatenate((vehicle_proportions, emissions.values[0]))

   #  with open(RESULTS_FILE, mode='a', encoding="utf-8") as file:
      #   writer = csv.writer(file)
      #   writer.writerow(combined)

    # Parse emissions (using parse_trip_emissions)
    total_PMx = parse_trip_emissions(TRIP_DATA_FILE)

    # Save results
    combined = np.concatenate((vehicle_proportions, [total_PMx]))

   # Check if the file exists to write a header if necessary
    file_exists = False
    try:
        with open(RESULTS_FILE, 'r', encoding="utf-8") as file:
            file_exists = True
    except FileNotFoundError:
        pass

   # Open the file in append mode and write data
    with open(RESULTS_FILE, mode='a', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
         # Write header if the file is being created
            writer.writerow(['pkw', 'bus', 'scooter', 'bike', 'total_PMx'])
            writer.writerow(combined)
        elif file_exists:
            writer.writerow(combined)

        print(f"Completed simulation {index} and saved results.")

print("Sensitivity study completed.")
