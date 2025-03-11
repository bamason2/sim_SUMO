# Summary

SUMO simulation files

* Tutorials - worked examples from SUMO tutorials on SUMO website
* Junctions - various junctions in HCMC 



## To Do

1. Case study selection

   a. Quickly select some candidate junctions in low air quality zones using satellite data

2. Emissions simulation options
   
   a. Aggregate vs time based? - does aggregate match integrated time based?  
   b. Does sample rate affect emissions calculations?
   c. Different type of vehicles - which vehicles should be included?
   d. Is there some data regarding vehicle types for HCMC or is observation required?
   e. Screening experiment - which factors to consider?
   f. Output is aggregate emissions and *through-flow*/*accumulation rate*?

3. Think about integration with MBC
   
   a. Investigate command line simulation and plotting
   b. Output file from MBC show factors and levels - what is the format?
   c. How to create configuration etc files for sumo according to experiment design
   d. Run multiple simulations and output results
   e. Preprocess results and put in a format that is suitable for mbc


## Code Automation

1. Use simpleT simulation with varying number of vehicles e.g. 1, 10, 100, 1000
2. Plot aggregate C02, NOx, PM(N).


