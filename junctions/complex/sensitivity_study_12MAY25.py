"Sensitivity study for SUMO simulation with defined routes"
# This script generates vehicle proportions using Sobol 
# sensitivity analysis and runs a SUMO simulation for each set 
# of proportions.


import csv
import subprocess
import sys
import numpy as np
import subprocess

from tools.experimental_design import sobol_sensitivity
from tools.random_route import generate_trip_file_defined_routes
from tools.sumo_interface import run_sumo_simulation, parse_trip_emissions

# Constants
TOTAL_VEHICLES = 1100

CONFIG_FILE = "complex_juntion.sumocfg"
NET_FILE = "complex_juntion.net.xml"
ROUTE_FILE = "complex_juntion.rou.xml"
TRIP_FILE = "complex_juntion.trips.xml"

SIMULATION_DURATION = 3600
RESULTS_FILE = "./complexJunction_sensitivity_results_12MAY25.csv"
EMISSION_FILE = "./emissions_data.xml"
TRIP_DATA_FILE = "./data.xml"

# Vehicle routes, as per the network
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
      "L8": ['L1', 'L10', 'L3', 'L4', 'L9']
   },
   "scooter": {
      "L2": ['L3', 'L7', 'L9'],
      "L22": ['L1', 'L3', 'L7', 'L9'],
      "L26": ['L1', 'L3', 'L7', 'L9'],
      "L8": ['L1', 'L3', 'L9']
   },
   "bike": {
      "L2": ['L3', 'L7', 'L9'],
      "L22": ['L1', 'L3', 'L7', 'L9'],
      "L26": ['L1', 'L3', 'L7', 'L9'],
      "L8": ['L1', 'L3', 'L9']
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
    generate_trip_file_defined_routes(
      trip_file=TRIP_FILE,
      total_vehicles=TOTAL_VEHICLES,
      duration=SIMULATION_DURATION,
      vehicle_proportions=vehicle_proportions,
      vehicle_routes=VEHICLE_ROUTES)

    try:
        subprocess.run([
         'duarouter',
         '--net-file', NET_FILE,
         '--route-files', TRIP_FILE,
         '--output-file', ROUTE_FILE
      ], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during routing: {e}")
        print(f"Error output: {e.stderr}")

   #  # Generate trip file from route file
   #  command = [
   #    'duarouter',
   #    '--verbose', 'true',
   #    '--net-file', NET_FILE,
   #    '--route-files', TRIP_FILE,
   #    '--output-file', ROUTE_FILE
   # ]

   #  # Run duarouter to generate routes
   #  subprocess.run(command, check=True)

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


