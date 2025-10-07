

"""
Sensitivity study with 8 parameters (single vType; all vehicles share same params per run).
Appends results to CSV after each simulation.
"""

"""
Sensitivity study with 8 parameters (single vType; all vehicles share same params per run).
Now writes CSV in real time (flush + fsync after each row).
"""

import os, sys, csv, subprocess, time, xml.etree.ElementTree as ET
import numpy as np

from tools.experimental_design import sobol_params, expected_samples
from tools.random_route import generate_trip_file_defined_routes
from tools.sumo_interface import run_sumo_simulation
from tools.analysis import parse_trip_emissions

# ---------- constants ----------
TOTAL_VEHICLES = 1500
SIMULATION_DURATION = 3600

CONFIG_FILE = "complex_junction.sumocfg"
NET_FILE = "complex_junction.net.xml"
TRIP_FILE = "complex_junction.trips.xml"
ROUTE_FILE = "complex_junction.rou.xml"

TRIP_DATA_FILE = "data.xml"                  # must match <tripinfo-output> in .sumocfg
RESULTS_FILE = "sobol_8params_results_3_OCT.csv"   # real-time append

VEHICLE_ROUTES = {
    "group1": {
        "L2": ["L3", "L7", "L9"],
        "L22": ["L1", "L3", "L7", "L9"],
        "L26": ["L1", "L3", "L7", "L9"],
        "L8": ["L1", "L3", "L9"],
    }   
}

# ---------- helper: count actual vehicles ----------
def count_spawned_vehicles(tripinfo_path: str) -> int:
    """Count how many <tripinfo> entries exist in SUMO tripinfo output."""
    if not os.path.exists(tripinfo_path):
        return 0
    try:
        tree = ET.parse(tripinfo_path)
        root = tree.getroot()
        return len(root.findall("tripinfo"))
    except ET.ParseError:
        return 0

def main():
    # ---------- design ----------
    BASE_SAMPLES = 512  # ~2448 runs (136 * (2*8+2))
    X, names, bounds = sobol_params(base_samples=BASE_SAMPLES, calc_second_order=True, seed=42)
    print(f"Expected total runs: {expected_samples(BASE_SAMPLES, True, k=len(names))}")
    print(f"Generated {X.shape[0]} Sobol samples for params {names}")

    #header = names + ["PMx"]
    header = names + ["PMx", "actual_vehicles", "runtime_sec"]

    # Prepare results CSV
    new_file = not os.path.exists(RESULTS_FILE)
    if new_file:
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f_init:
            w_init = csv.writer(f_init)
            w_init.writerow(header)

    # Open in append mode (line-buffered)
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8", buffering=1) as f:
        w = csv.writer(f)

        # ---------- simulation loop ----------
        for i, row in enumerate(X):
            params = {names[j]: float(row[j]) for j in range(len(names))}

            print("\n" + "=" * 70)
            print(f"Run {i+1}/{len(X)} | {TOTAL_VEHICLES} vehicles | Duration={SIMULATION_DURATION}s")
            short_params = ", ".join(f"{k}={params[k]:.1f}" for k in names)
            print(f"Parameters: {short_params}")

            # a) generate trips
            generate_trip_file_defined_routes(
                trip_file=TRIP_FILE,
                total_vehicles=TOTAL_VEHICLES,
                duration=SIMULATION_DURATION,
                vehicle_routes=VEHICLE_ROUTES,
                vtype_params=params,
                seed=123 + i,
            )

            # b) duarouter
            try:
                subprocess.run(
                    ["duarouter", "--net-file", NET_FILE, "--route-files", TRIP_FILE, "--output-file", ROUTE_FILE],
                    check=True, capture_output=True, text=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] duarouter failed at sample {i}")
                print(e.stderr)
                w.writerow(list(row) + [np.nan, 0, 0])
                f.flush()
                os.fsync(f.fileno())
                continue  # skip to next run

            # c) run SUMO and measure runtime
            start_time = time.perf_counter()
            run_sumo_simulation(CONFIG_FILE)
            runtime_sec = time.perf_counter() - start_time

            # d) parse PMx and actual vehicles
            pmx = parse_trip_emissions(TRIP_DATA_FILE)
            actual_vehicles = count_spawned_vehicles(TRIP_DATA_FILE)

            # e) save results
            w.writerow(list(row) + [pmx, actual_vehicles, round(runtime_sec, 2)])
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass

            # f) log summary
 #           print(f" → Completed [{i+1}/{len(X)}] | PMx={pmx:.4f} | Vehicles appeared={actual_vehicles}/{TOTAL_VEHICLES} | Runtime={runtime_sec:.2f}s")
            print(f" → Completed [{i+1}/{len(X)}] | PMx={pmx:.4f} ")

    print(f"\nAll results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()