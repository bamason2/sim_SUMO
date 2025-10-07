"""Some functions providing an interface to SUMO"""

import subprocess

def run_sumo_simulation(config_file):
    """Run SUMO simulation with the specified configuration file"""
    sumo_command = ["sumo", "-c", config_file]
    subprocess.run(sumo_command, check=False)
