# ==========================================================
# Hydraulic Simulation Example 2
# - Modify Decision variable: pump status at every time-step
# - Check constraints: nodal pressure
# - using EN_Mod Python-EPANET Interface
# ===========================================================
import numpy as np
from EN_Mod import *

# Open the EPANET toolkit to analyse WDN
NET_size = ENopen('CalNet.inp','CalNet.rpt','')
print(NET_size)

# number of nodes and links
nnodes = int(NET_size['nodes'])
nlinks = int(NET_size['links'])

# Get number of patterns and controls
npat = ENgetcount(EN_PATCOUNT)
nctrls = ENgetcount(EN_CONTROLCOUNT)
# Control storage Matrix
ctrlMaster = []

# Populate Matrix with control rule properties 
for j in range(nctrls):
    [ctype,lindex,setting,nindex,level] = ENgetcontrol(j+1)
    if nindex!= 0:           
        ctrlMaster.append([ctype,ENgetlinkid(int(lindex)),setting,ENgetnodeid(int(nindex)),level])
    else:             # case where no controlling node (time-based controls)
        ctrlMaster.append([ctype,lindex,setting,nindex,level])
