import emod_api.dtk_tools.demographics.DemographicsHelperFunctions as helpers
"""
This file is just a very notional attempt to exercises the script imported above, which is code gathered from research. At this time nothing good happens when you run this.
"""

#print( helpers.ConstructNodesFromDataFrame(node_info, extra_data_columns = [], res=30/3600) ) # By default, set node ID using lat long.  Should we allow a node ID field to be in the dataframe, instead?
#print( helpers.SpatialLoadBalancing(nCores=4, nodeInfoTable, outFile="slb") )
#print( helpers.fill_nodes_legacy(node_info, DemoDf, res=30/3600) )
try:
    print( helpers.AdjustPopsToStartDate(nodes=[], PopFile="pop_file.csv", StartYear=1972) )
except Exception as ex:
    print( str( ex ) )

try:
    print( helpers.BuildInterpolatedBirthRateMap_UniformDemog(PopFile="pop_file.csv", DemoFile="demog.json", StartYear=1972, Duration=10, country='Nigeria') )
except Exception as ex:
    print( str( ex ) )

try:
    print( helpers.BuildInterpolatedBirthRateMap_HeterogeneousDemog(population_filename="pop_file.csv", demographics_filename="demog.json") )
except Exception as ex:
    print( str( ex ) )

print( helpers.computeMortalityDist(dot_name="dot.dot", DemoDf="demog.json") )
print( helpers.MortalityAndAgeDistributions(dot_name="dot.dot", DemoDf="demog.json", birthRate=0.123) )
print( helpers.computeAgeDist(bval=1.0,mvecX=[],mvecY=[],fVec=[]) )

