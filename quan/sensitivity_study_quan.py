import csv
import subprocess
import sys
import numpy as np

#sys.path.append('/home/quan/Desktop/sim_SUMO/tools')  # path to the tools directory
#from experimental_design import sobol_sensitivity
##from random_route import generate_route_file_defined_routes
#from sumo_interface import run_sumo_simulation, parse_emission_data

#TOTAL_VEHICLES = 1000
#CONFIG_FILE = "./complex_juntion.sumocfg"
#NET_FILE = "./complex_juntion.net.xml"
#ROUTE_FILE = "./complex_juntion.rou.xml"
#SIMULATION_DURATION = 3600
#RESULTS_FILE = "./sensitivity_results.csv"
#EMISSION_FILE = "./emissions_data.xml"
sys.path.append(r'C:/Users/Nguyen Minh Quan/Quan/Quan/Desktop/SUMO simulation/sim_SUMO/tools')  #path to the tools directory
from experimental_design import sobol_sensitivity
from random_route import generate_route_file_defined_routes
from sumo_interface import run_sumo_simulation, parse_emission_data

TOTAL_VEHICLES = 1000
CONFIG_FILE = r"C:\Users\Nguyen Minh Quan\Quan\Quan\Desktop\SUMOsimulation\sim_SUMO\quan\complex.sumocfg"
NET_FILE = r"C:\Users\Nguyen Minh Quan\Quan\Quan\Desktop\SUMOsimulation\sim_SUMO\quan\complex.net.xml"
ROUTE_FILE = r"C:\Users\Nguyen Minh Quan\Quan\Quan\Desktop\SUMOsimulation\sim_SUMO\quan\complex.rou.xml"
#TRIP_FILE = "./complex_juntion.trips.xml"
SIMULATION_DURATION = 3600
RESULTS_FILE = "./sensitivity_results.csv"
EMISSION_FILE = "./emissions_data.xml"
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
      "L5": ['L1', 'L3', 'L4', 'L7', 'L9'],
      "L8": ['L1', 'L3', 'L9']
   },
   "bike": {
      "L2": ['L3', 'L7', 'L9'],
      "L22": ['L1', 'L3', 'L7', 'L9'],
      "L26": ['L1', 'L3', 'L7', 'L9'],
      "L5": ['L1', 'L3', 'L4', 'L7', 'L9'],
      "L8": ['L1', 'L3', 'L9']
   }
}

# Generate the vehicle proportions for the sensitivity study
vehicle_counts = sobol_sensitivity(total_vehicles=TOTAL_VEHICLES)

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
        '--net-file', './complex_juntion.net.xml',
        '--route-files', './complex_juntion.rou.xml',
        '--output-file', './complex_juntion_output.rou.xml'
    ]
    
    # Run duarouter to generate routes
    subprocess.run(command, check=True)

    # Run simulation
    print(f"Running simulation {index}...")
    run_sumo_simulation(config_file=CONFIG_FILE)

    # Parse emissions
    emissions = parse_emission_data(emission_file=EMISSION_FILE)

    # Save results
    combined = np.concatenate((vehicle_proportions, emissions.values[0]))

    with open(RESULTS_FILE, mode='a', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(combined)

    print(f"Completed simulation {index} and saved results.")

print("Sensitivity study completed.")
