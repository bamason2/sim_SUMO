# """Some functions providing an interface to SUMO"""

# import subprocess

# def run_sumo_simulation(config_file):
#     """Run SUMO simulation with the specified configuration file"""
#     sumo_command = ["sumo", "-c", config_file]
#     subprocess.run(sumo_command, check=False)

## thu code chay 10 behavior params
"""
Small helper to run SUMO with a .sumocfg file.
"""

import subprocess

def run_sumo_simulation(config_file: str, gui: bool = False) -> None:
    """
    Run SUMO or SUMO-GUI with the given configuration.
    Requires SUMO binaries in PATH.
    """
    cmd = ["sumo-gui" if gui else "sumo", "-c", config_file]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("[ERROR] SUMO failed")
        print(e.stderr)
        raise

