"""
Saltelli/Sobol sampling for 10 driver/behavior parameters.
All sampled values are rounded to 1 decimal place (0.1 step).

Parameters (k = 10) & bounds:
- acceleration: [4, 10]
- deceleration: [6, 12]
- sigma: [0, 1]
- minGap: [0.3, 2.5]
- lcSpeedGain: [0, 5.3]
- lcCooperative: [0, 1]
- lcPushy: [0, 1]
- lcStrategic: [0, 5.9]
- lcAssertive: [0, 2.5]
- jmDriveAfterYellowTime: [-1, 4]
"""

from typing import Tuple, List, Optional
import numpy as np
from SALib.sample import saltelli

NAMES = [
    "acceleration",
    "deceleration",
#    "sigma",
    "minGap",
    "lcSpeedGain",
    "lcCooperative",
    "lcPushy",
    "lcStrategic",
    "lcAssertive",
#    "jmDriveAfterYellowTime",
]

BOUNDS = [
    [4.0, 10.0],   # acceleration
    [6.0, 12.0],   # deceleration
    [0.3, 2.5],    # minGap
    [0.0, 5.3],    # lcSpeedGain
    [0.0, 1.0],    # lcCooperative
    [0.0, 1.0],    # lcPushy
    [0.0, 5.9],    # lcStrategic
    [0.0, 2.5],    # lcAssertive

]

def build_problem() -> dict:
    return {"num_vars": len(NAMES), "names": NAMES, "bounds": BOUNDS}

def expected_samples(base_samples: int, calc_second_order: bool = True, k: int = len(NAMES)) -> int:
    if base_samples <= 0:
        raise ValueError("base_samples must be > 0")
    return base_samples * (2 * k + 2) if calc_second_order else base_samples * (k + 2)

def _round_and_clip(X: np.ndarray, bounds: List[List[float]], decimals: int = 3) -> np.ndarray:
    """Round to given decimals then clip each column into its bounds."""
    Xr = np.round(X, decimals=decimals)
    for j, (lo, hi) in enumerate(bounds):
        Xr[:, j] = np.clip(Xr[:, j], lo, hi)
    return Xr

def sobol_params(
    base_samples: int = 200,        # 200 * 22 = 4400 (~4500)
    calc_second_order: bool = True,
    seed: Optional[int] = None,
    decimals: int = 3,              # keep 3 decimal places
) -> Tuple[np.ndarray, List[str], List[List[float]]]:
    """
    Return X (N x 10), names, bounds.
    X is rounded to `decimals` places and clipped into bounds.
    """
    if seed is not None:
        np.random.seed(seed)

    problem = build_problem()
    X = saltelli.sample(problem, N=base_samples, calc_second_order=calc_second_order)

    if X.ndim != 2 or X.shape[1] != problem["num_vars"]:
        raise RuntimeError(f"Unexpected Saltelli output shape: {X.shape}, expected (*, {problem['num_vars']})")

    X = _round_and_clip(X, problem["bounds"], decimals=decimals)
    return X, problem["names"], problem["bounds"]

# Quick CLI to dump design
if __name__ == "__main__":
    import csv
    BASE = 200
    CALC2 = True
    X, names, _ = sobol_params(base_samples=BASE, calc_second_order=CALC2, seed=42, decimals=1)
    print("Expected total:", expected_samples(BASE, CALC2, k=len(names)))
    print("Generated:", X.shape)
    with open("sobol_8params_design.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(names); w.writerows(X.tolist())
    print("Saved to sobol_8params_design.csv")
