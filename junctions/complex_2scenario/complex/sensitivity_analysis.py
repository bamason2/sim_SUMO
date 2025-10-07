"""Results analysis of complex junction sensitivity analysis
complexJunction_sensitivity_results_12MAY25.csv
"""

from SALib.analyze import sobol
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
import pandas as pd
import numpy as np
from tools.analysis import display_table

# set results file
RESULTS_FILE = "complexJunction_sensitivity_results_4AUG25c.csv"
ROUTE_FILE = "complex_juntion.rou.xml"


# Define problem with 4 independent vars
problem = {
    'num_vars': 4,
    'names': ['pkw', 'bus', 'scooter', 'trailer'],
    'bounds': [[0, 1]] * 4
}

# read in the csv file output from simulations
data = np.genfromtxt(RESULTS_FILE, delimiter=',', skip_header=0)

X = data[:, 0:3]  # input variables
Y = data[1:, 4]  # output variable (excluding the header)

# convert Y to np array
Y = np.array(Y)

# Run sobol sensitivity analysis
Si = sobol.analyze(problem, Y, calc_second_order=True, print_to_console=True)

# Display results as tables
#----------------------------------------------
first_order_df = pd.DataFrame({
    'Parameter': problem['names'],
    'S1': Si['S1'],
    'S1_conf': Si['S1_conf'],
    'ST': Si['ST'],
    'ST_conf': Si['ST_conf']
})

second_order = []
for i, name_i in enumerate(problem['names']):
    for j, name_j in enumerate(problem['names']):
        if j > i:
            s2 = Si['S2'][i, j]
            s2_conf = Si['S2_conf'][i, j]
            if s2 is not None and abs(s2) > 1e-4:
                second_order.append({
                    'Param 1': name_i,
                    'Param 2': name_j,
                    'S2': s2,
                    'S2_conf': s2_conf
                })
second_order_df = pd.DataFrame(second_order)

# Round for display
first_order_df = round(first_order_df, 3)
second_order_df = round(second_order_df, 3)

# Display as tables
display_table(first_order_df, title="First and Total-order Sobol Indices")
display_table(second_order_df, title="Second-order Sobol Indices (Non-zero)")

# Visualise results (main effects) as bar plot
#----------------------------------------------
labels = ['pkw', 'bus', 'scooter', 'trailer']


S1 = Si['S1']
ST = Si['ST']

x = np.arange(len(labels))
width = 0.35

plt.bar(x - width/2, S1, width, label='Main Effect')
plt.bar(x + width/2, ST, width, label='Total Effect')
plt.xticks(x, labels)
plt.ylabel('Sensitivity Index')
plt.title('Sobol Sensitivity Analysis (PMx)')
plt.legend()
plt.tight_layout()
plt.show()


# Plot scatter plots of each vehicle type vs PMx
#----------------------------------------------

df = pd.DataFrame(data[1:, 0:4], columns=labels) # vehicle proportions
df['PMx'] = data[1:, 4]  # PMx

# Set up 2x2 grid of plots
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

for i, var in enumerate(labels):
    x = df[var]
    y = df['PMx']

    # Plot scatter and regression line
    sns.regplot(x=x, y=y, ax=axes[i],
                scatter_kws={'alpha': 0.4},
                line_kws={'color': 'red'})

    # Spearman correlation
    rho, pval = spearmanr(x, y)

    # Gradient (slope) of the linear fit
    slope, intercept = np.polyfit(x, y, deg=1)

    # Title with correlation and gradient
    axes[i].set_title(
        f'{var} vs PMx\n'
        f'Spearman r = {rho:.3f}, p = {pval:.3g}, slope = {slope:.3f}'
    )
    axes[i].set_xlabel(f'{var} proportion')
    axes[i].set_ylabel('PMx')

plt.tight_layout()
plt.show()


# plot the start times for each vehicle as a stacked bar chart (one example from simulation)
#----------------------------------------------
# info = get_vehicle_info(route_file=ROUTE_FILE)
# plot_departure_histogram_by_type(info, 3600, num_bins=60)
