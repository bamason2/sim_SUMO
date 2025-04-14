from random_route import get_sinks_and_sources

import sys
sys.path.append('/Users/byronmason/Code/sim_SUMO/tools')  #path to the tools directory


NET_FILE = "complex_juntion.net.xml"

sinks, sources = get_sinks_and_sources(NET_FILE)


print("Sinks: ", sinks)
print("Sources: ", sources)