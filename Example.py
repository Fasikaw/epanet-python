import numpy as np
from EN_Mod import *
# ====================================================
# Hydraulic Simulation Example 
# - using EN_Mod Python-EPANET Interface
# ====================================================

# Open the EPANET toolkit to analyse WDN
NET_size = ENopen('BMV.inp','BMV.rpt','')
print(NET_size)
# number of nodes and links
nnodes = int(NET_size['nodes'])
nlinks = int(NET_size['links'])

# Initialise lists of node and pipe IDs
node_IDs = []
link_IDs = []
pump_Index = []

# Populate lists of node and link IDs and types in format [{ID:type},..]
for index in range(nlinks):
    link_IDs.append({ENgetlinkid(index+1):ENgetlinktype(index+1)})
    if index < nnodes:
        node_IDs.append({ENgetnodeid(index+1):ENgetnodetype(index+1)})
    if str(ENgetlinktype(index+1)) == 'PUMP':
        pump_Index.append(ENgetlinkindex((ENgetlinkid(index+1))))

# Get simulation timestep properties
sim_dur = ENgettimeparam(EN_DURATION)/3600
# Get hydraulic timestep
t = 0
dt = ENgettimeparam(EN_HYDSTEP)/3600
pstep = ENgettimeparam(EN_PATTERNSTEP)/3600
sim_time = []

# Matrix of daily nodal pressures
nodal_P = np.empty([sim_dur*2,nnodes],dtype = float)
# Matrix of daily link flows
link_F = np.empty([sim_dur*2,nlinks],dtype=float)
# Array of daily pump status
PumpStat = np.empty([sim_dur*2,len(pump_Index)],dtype=int)
# Master output
MasterOut = np.empty([sim_dur*2,63])

# Launch and Initialise Hydraulic Analysis
ENopenH()
ENinitH(0)          # 0 indicates not to write to hydraulics report

while dt > 0:
    # Compute hydraulics
    ENrunH()
    # Get current simulation time
    sim_time.append(ENsimtime())
    # Get calculated network properties - iterate through all indices
    for index in range(nlinks):
        # Get flow of pipe 
        link_F[t,index] = ENgetlinkvalue(index+1,EN_FLOW)
        if (index+1) == pump_Index[0]:
            # record if pump 1 is turned on
            PumpStat[t,0] = ENgetlinkvalue(index+1,EN_STATUS)
        elif(index+1) == pump_Index[1]:
            # record if pump 2 is turned on
            PumpStat[t,1] = ENgetlinkvalue(index+1,EN_STATUS)
        if index < nnodes:
            # Get head at node
            nodal_P[t,index] = ENgetnodevalue(index+1,EN_HEAD)
    # get next timestep
    dt = ENnextH()
    #increment counter
    t += 1
ENcloseH()

# Compile output into Master matrix
MasterOut[0:t,0] = range(t)
MasterOut[0:t,1:3] = PumpStat[0:t,0:2]
MasterOut[0:t,4:29] = nodal_P[0:t,:]
MasterOut[0:t,30:63] = link_F[0:t,:]
# Write to text file
np.savetxt('Hyd_summ.txt',MasterOut[0:t,:])    