# -*- coding: utf-8 -*-
# Provides C compatible data types, and allows calling functions in DLLs or shared libraries. 
import ctypes   
import os
import datetime

# Establish current directory
script_dir = os.path.dirname(__file__)
dll_dir = os.path.join(script_dir,'epanet2.dll')

# Verify that DLL exists in current working directory
if os.path.exists(dll_dir):
    # Load DLL into memory using ctypes
    _lib = ctypes.cdll.epanet2
else:
    raise Exception('epanet2.dll does not exist in working directory.')

# Specify error and ID_label character lengths
_max_label_len= 32
_err_max_char= 80

_current_simulation_time=  ctypes.c_long()

# ============================================================================================================
# Open/Close Toolkit Operations
# ============================================================================================================
def ENopen(inpname, repname='report.txt', binname=''):
    # Description:
    #     Opens the Toolkit to analyze a particular distribution system.
    #     Defines global structure EN_SIZE.
    # Arguments:
    #     inpname:	name of an EPANET Input file
    #     repname:	name of an output Report file
    #     binname:	name of an optional binary Output file.
    # Returns:
    #     Returns a dictionary of network size (number of nodes, links and tanks)
    #     Outputs to console if network was successfully launched
    
    errcode = _lib.ENopen(ctypes.c_char_p(inpname), ctypes.c_char_p(repname), ctypes.c_char_p(binname))
    if errcode!=0: 
        raise ENtoolkitError(errcode)
    else:
        print('The %s Network has been successfully launched!'%(inpname))
        # Get properties of network - number of nodes,links, tanks
        nnodes = ENgetcount(EN_NODECOUNT)
        nlinks = ENgetcount(EN_LINKCOUNT)
        ntanks = ENgetcount(EN_TANKCOUNT)
    return {'nodes':nnodes, 'links':nlinks, 'tanks':ntanks}

def ENclose():
   # Description:
   #   Closes down the Toolkit system (including all files being processed).
   # Returns:
   #   Returns an error code.
   # Notes:
   #   ENclose must be called when all processing has been completed,
   #   even if an error condition was encountered.
   errcode = _lib.ENclose()
   if errcode!=0: raise ENtoolkitError(errcode)
# ============================================================================================================
# Nodal manipulation
# ============================================================================================================
def ENgetnodeindex(nodeid):
   # Description:
   #     Retrieves the index of a node with a specified ID.
   # Arguments:
   #     id:	node ID label
   # Returns:
   #     Returns an error code.
   #     index: node index
   # Notes:
   #     Node indexes are consecutive integers starting from 1.
    j= ctypes.c_int()
    errcode = _lib.ENgetnodeindex(ctypes.c_char_p(nodeid), ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENgetnodeid(index):
   # Description:
   #    Retrieves the ID label of a node with a specified index.
   # Arguments:
   #    index:	node index
   # Returns:
   #    Returns an error code. 
   #    id:ID label of node
   # Notes:
   #    The ID label string should be sized to hold at least 15 characters.   
    label = ctypes.create_string_buffer(_max_label_len)
    errcode= _lib.ENgetnodeid(index, ctypes.byref(label))
    if errcode!=0: raise ENtoolkitError(errcode)
    return label.value

def ENgetnodetype(index):
   # Description:
   #    Retrieves the node-type code for a specific node.
   # 
   # Arguments:
   #    index:	        node index
   #    typecode:	node-type code (see below)
   # 
   # Returns:
   #    Returns an error code.
   #    Retrieves the node-type code for a specific node
   #
   # Notes:
   #    Node indexes are consecutive integers starting from 1.
   #    Node type codes consist of the following constants:
   # 
   # EN_JUNCTION	0	Junction node
   # EN_RESERVOIR	1	Reservoir node
   # EN_TANK	        2	Tank node
    j= ctypes.c_int()
    errcode= _lib.ENgetnodetype(index, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    node_type = {'0':'Junction', '1':'Reservoir', '2':'Tank'}
    return node_type[str(j.value)]

def ENgetnodevalue(index, paramcode):
    # Description:
    # Retrieves the parameter value of a specific link parameter.
    #
    # Arguments:
    # index:     node index
    # paramcode: Node parameter codes consist of the following constants:
    #              EN_ELEVATION      Elevation
    #              EN_BASEDEMAND     ** Base demand
    #              EN_PATTERN        ** Demand pattern index
    #              EN_EMITTER        Emitter coeff.
    #              EN_INITQUAL       Initial quality
    #              EN_SOURCEQUAL     Source quality
    #              EN_SOURCEPAT      Source pattern index
    #              EN_SOURCETYPE     Source type (See note below)
    #              EN_TANKLEVEL      Initial water level in tank
    #              EN_DEMAND         * Actual demand
    #              EN_HEAD           * Hydraulic head
    #              EN_PRESSURE       * Pressure
    #              EN_QUALITY        * Actual quality
    #              EN_SOURCEMASS     * Mass flow rate per minute of a chemical source
    #                * computed values
    #               ** primary demand category is last on demand list

    #          The following parameter codes apply only to storage tank nodes:
    #              EN_INITVOLUME  Initial water volume
    #              EN_MIXMODEL    Mixing model code (see below)
    #              EN_MIXZONEVOL  Inlet/Outlet zone volume in a 2-compartment tank
    #              EN_TANKDIAM    Tank diameter
    #              EN_MINVOLUME   Minimum water volume
    #              EN_VOLCURVE    Index of volume versus depth curve (0 if none assigned)
    #              EN_MINLEVEL    Minimum water level
    #              EN_MAXLEVEL    Maximum water level
    #              EN_MIXFRACTION Fraction of total volume occupied by the inlet/outlet zone in a 2-compartment tank
    #              EN_TANK_KBULK  Bulk reaction rate coefficient"""
    j= ctypes.c_float()
    errcode= _lib.ENgetnodevalue(index, paramcode, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value
    
def ENsetnodevalue(index, paramcode, value):
   # Description:
   # Sets the value of a parameter for a specific node.
   # 
   # Arguments:
   # index:		node index
   # paramcode:		parameter code (see below)
   # value:	parameter value
   # 
   # Returns:
   # Returns an error code.
   # 
   # Notes:
   # Node indexes are consecutive integers starting from 1.
   # Node parameter codes consist of the following constants:
   # 
   # EN_ELEVATION	0	Elevation
   # EN_BASEDEMAND	1	Baseline demand
   # EN_PATTERN	        2	Time pattern index
   # EN_EMITTER	        3	Emitter coefficient
   # EN_INITQUAL	4	Initial quality
   # EN_SOURCEQUAL	5	Source quality
   # EN_SOURCEPAT	6	Source pattern
   # EN_SOURCETYPE	7	Source type:(See note below)
   # EN_TANKLEVEL	8	Initial water level in tank
   # Source types are identified with the following constants:
   # 
   # EN_CONCEN	        0
   # EN_MASS	        1
   # EN_SETPOINT	2
   # EN_FLOWPACED	3
   # See [SOURCES] for a description of these source types.
   # 
   # Values are supplied in units which depend on the units used for flow rate in the EPANET input file (see Units of Measurement).
    errcode= _lib.ENsetnodevalue(ctypes.c_int(index), ctypes.c_int(paramcode), ctypes.c_float(value))
    if errcode!=0: raise ENtoolkitError(errcode)
    
# ============================================================================================================
# Link Manipulation
# ============================================================================================================
def ENgetlinkindex(linkid):
    # Description: Retrieves the index of a link with a specified ID.
    # Arguments: linkid: link ID label
    # Returns:link index
    j= ctypes.c_int()
    errcode= _lib.ENgetlinkindex(ctypes.c_char_p(linkid), ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENgetlinkid(index):
    # Description: Retrieves the ID label of a link with a specified index.
    # Arguments: index: link index
    # Returns: linkid: link ID label
    label = ctypes.create_string_buffer(_max_label_len)
    errcode= _lib.ENgetlinkid(index, ctypes.byref(label))
    if errcode!=0: raise ENtoolkitError(errcode)
    return label.value

def ENgetlinktype(index):
    # Description: Retrieves the link-type code for a specific link.
    # Arguments: index: link index
    # Returns: link type index   
    #Note:
    # Link types:
    # EN_CVPIPE        = 0      
    # EN_PIPE          = 1
    # EN_PUMP          = 2
    # EN_PRV           = 3
    # EN_PSV           = 4
    # EN_PBV           = 5
    # EN_FCV           = 6
    # EN_TCV           = 7
    # EN_GPV           = 8
    j= ctypes.c_int()
    errcode= _lib.ENgetlinktype(index, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    link_type = {'0':'CVPIPE', '1':'PIPE', '2':'PUMP','3':'PRV','4':'PSV','5':'PBV','6':'FCV', '7':'TCV', '8':'GPV'}
    return link_type[str(j.value)]

def ENgetlinknodes(index):
    # Description: Retrieves the indexes of the end nodes of a specified link.
    # Arguments: index: link index
    # Returns: integer indices of end nodes
    j1= ctypes.c_int()
    j2= ctypes.c_int()
    errcode= _lib.ENgetlinknodes(index,ctypes.byref(j1),ctypes.byref(j2))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j1.value,j2.value

def ENgetlinkvalue(index, paramcode):
    # Description: Retrieves the value (type = float) of a specific link parameter.
    # Arguments:
    # index:     link index
    # paramcode: Link parameter codes consist of the following constants:
    #             EN_DIAMETER     Diameter
    #             EN_LENGTH       Length
    #             EN_ROUGHNESS    Roughness coeff.
    #             EN_MINORLOSS    Minor loss coeff.
    #             EN_INITSTATUS   Initial link status (0 = closed, 1 = open)
    #             EN_INITSETTING  Roughness for pipes, initial speed for pumps, initial setting for valves
    #             EN_KBULK        Bulk reaction coeff.
    #             EN_KWALL        Wall reaction coeff.
    #             EN_FLOW         * Flow rate
    #             EN_VELOCITY     * Flow velocity
    #             EN_HEADLOSS     * Head loss
    #             EN_STATUS       * Actual link status (0 = closed, 1 = open)
    #             EN_SETTING      * Roughness for pipes, actual speed for pumps, actual setting for valves
    #             EN_ENERGY       * Energy expended in kwatts
    #               * computed values
    j= ctypes.c_float()
    errcode= _lib.ENgetlinkvalue(index, paramcode, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENsetlinkvalue(index, paramcode, value):
    # Sets the value of a parameter for a specific link.
    # Arguments:
    # index:  link index
    # paramcode: Link parameter codes consist of the following constants:
    #             EN_DIAMETER     Diameter
    #             EN_LENGTH       Length
    #             EN_ROUGHNESS    Roughness coeff.
    #             EN_MINORLOSS    Minor loss coeff.
    #             EN_INITSTATUS   * Initial link status (0 = closed, 1 = open)
    #             EN_INITSETTING  * Roughness for pipes, initial speed for pumps, initial setting for valves
    #             EN_KBULK        Bulk reaction coeff.
    #             EN_KWALL        Wall reaction coeff.
    #             EN_STATUS       * Actual link status (0 = closed, 1 = open)
    #             EN_SETTING      * Roughness for pipes, actual speed for pumps, actual setting for valves
    #             * Use EN_INITSTATUS and EN_INITSETTING to set the design value for a link's status or setting that 
    #               exists prior to the start of a simulation. Use EN_STATUS and EN_SETTING to change these values while 
    #               a simulation is being run (within the ENrunH - ENnextH loop).
    # value:parameter value
    errcode= _lib.ENsetlinkvalue(ctypes.c_int(index), ctypes.c_int(paramcode), ctypes.c_float(value))
    if errcode!=0: raise ENtoolkitError(errcode)
    
# ============================================================================================================
# Pattern Manipulation
# ============================================================================================================
def ENgetpatternid(index):
    # Description: Retrieves the ID label of a particular time pattern.
    # Arguments:
    # index: pattern index
    label = ctypes.create_string_buffer(_max_label_len)
    errcode= _lib.ENgetpatternid(index, ctypes.byref(label))
    if errcode!=0: raise ENtoolkitError(errcode)
    return label.value

def ENgetpatternindex(patternid):
    # Description: Retrieves the index of a particular time pattern.
    # Arguments:
    # id: pattern ID label
    j= ctypes.c_int()
    errcode= _lib.ENgetpatternindex(ctypes.c_char_p(patternid), ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENgetpatternlen(index):
    # Description: Retrieves the number of time periods in a specific time pattern.
    # Arguments:
    # index: pattern index
    j= ctypes.c_int()
    errcode= _lib.ENgetpatternlen(index, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENgetpatternvalue( index, period):
    # Description: Retrieves the multiplier factor for a specific time period in a time pattern.
    # Arguments:
    #     index:time pattern index
    #     period: period within time pattern
    j= ctypes.c_float()
    errcode= _lib.ENgetpatternvalue(index, period, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENaddpattern(patternid):
    # Description: Adds a new time pattern to the network.
    # Arguments: id: ID label of pattern 
    # Notes: 
    #      The ID label should contain no more than 31 characters.  
    #      The new pattern will contain a single time period whose multiplier factor is 1.  
    #      Use the ENsetpattern function to populate the pattern with a specific set of multipliers after first retrieving its index with the ENgetpatternindex function.  
    # Example: 
    #      char  patId[] = "NewPattern";  
    #      float patFactors[] = {0.8, 1.1, 1.4, 1.1, 0.8, 0.7};  
    #      int   patIndex;  
    #      ENaddpattern(patId);  
    #      ENgetpatternindex(patId, patIndex);  
    #      ENsetpattern(patIndex, patFactors, 6);
    errcode= _lib.ENaddpattern(ctypes.c_char_p(patternid))
    if errcode!=0: raise ENtoolkitError(errcode)

def ENsetpattern(index, factors):
    # Description: Sets all of the multiplier factors for a specific time pattern.
    # Arguments:
    #     index:    time pattern index
    #     factors:  multiplier factors list for the entire pattern
    # Notes:
    #      Pattern indexes are consecutive integers starting from 1.  
    #     factors points to a zero-based array that contains nfactors elements.  
    #     Use this function to redefine (and resize) a time pattern all at once; 
    #     use ENsetpatternvalue to revise pattern factors in specific time periods of a pattern.  
    nfactors= len(factors)
    cfactors_type= ctypes.c_float* nfactors
    cfactors= cfactors_type()
    for i in range(nfactors):
       cfactors[i]= float(factors[i] )
    errcode= _lib.ENsetpattern(ctypes.c_int(index), cfactors, ctypes.c_int(nfactors) )
    if errcode!=0: raise ENtoolkitError(errcode)

def ENsetpatternvalue( index, period, value):
    # Description: Sets the multiplier factor for a specific period within a time pattern.
    # Arguments:
    #   index: time pattern index
    #   period: period within time pattern
    #   value:  multiplier factor for the period
    # Pattern indexes and periods are consecutive integers starting from 1.
    errcode= _lib.ENsetpatternvalue( ctypes.c_int(index), ctypes.c_int(period), ctypes.c_float(value) )
    if errcode!=0: raise ENtoolkitError(errcode)
 
# ============================================================================================================
# Control Rule Manipulation
# ============================================================================================================

def ENgetcontrol(cindex):
    # Declaration:
    #     [errcode, ctype,lindex,setting,nindex,level] = ENgetcontrol(cindex)
    # 
    # Description:
    #      Retrieves the parameters of a simple control statement. The index of the
    #      control is specified in cindex and the remaining arguments return the 
    #      control's parameters.   
    # 
    # Arguments: 
    #      cindex:  control statement index 
    #      ctype:   control type code 
    #      lindex:  index of link being controlled 
    #      setting: value of the control setting 
    #      nindex:  index of controlling node 
    #      level:   value of controlling water level or pressure for 
    #               level controls or of time of control action 
    #               (in seconds) for time-based controls 
    #
    # Returns:
    #  Returns an error code.
    # 
    # Notes:
    #  Controls are indexed starting from 1 in the order in which they 
    #  were entered into the [CONTROLS] section of the EPANET input file. 
    #
    # Control type codes consist of the following:  
    #   - 0 (Low Level Control) applies when tank level or node pressure drops below specified level 
    #   - 1 (High Level Control) applies when tank level or node pressure rises above specified level 
    #   - 2 (Timer Control) applies at specific time into simulation 
    #   - 3 (Time-of-Day Control) applies at specific time of day 
    #
    # For pipes, a setting of 0 means the pipe is closed and 1 means it is open.
    # For a pump, the setting contains the pump's speed, with 0 meaning the pump
    # is closed and 1 meaning it is open at its normal speed.
    # For a valve, the setting refers to the valve's pressure, flow, or loss 
    # coefficient value, depending on valve type.
    #
    # For Timer or Time-of-Day controls the nindex parameter equals 0.  
    #
    # See ENsetcontrol for an example of using this function. 
    ctype = ctypes.c_int()
    lindex = ctypes.c_int()
    setting = ctypes.c_float()
    nindex = ctypes.c_int()
    level = ctypes.c_float()
    
    errcode= _lib.ENgetcontrol(cindex, ctypes.byref(ctype), 
                            ctypes.byref(lindex), ctypes.byref(setting), 
                            ctypes.byref(nindex), ctypes.byref(level))
    if errcode!=0: raise ENtoolkitError(errcode)
    return [ctype.value,lindex.value, setting.value,nindex.value,level.value]
    
def ENsetcontrol(cindex, ctype, lindex, setting, nindex, level ):
    # Description:
    #      Sets the parameters of a simple control statement.  
    # 
    # Arguments: 
    #      cindex:  control statement index 
    #      ctype:   control type code 
    #      lindex:  index of link being controlled 
    #      setting: value of the control setting 
    #      nindex:  index of controlling node 
    #      level:   value of controlling water level or pressure for 
    #               level controls or of time of control action 
    #               (in seconds) for time-based controls 
    #
    # Returns:
    #      Returns an error code.
    # 
    # Notes:
    #     Controls are indexed starting from 1 in the order in which they were 
    #     entered into the [CONTROLS] section of the EPANET input file.  
    #
    # Control type codes consist of the following:  
    #      EN_LOWLEVEL      0   Control applied when tank level or node pressure drops below specified level 
    #      EN_HILEVEL       1   Control applied when tank level or node pressure rises above specified level 
    #      EN_TIMER         2   Control applied at specific time into simulation 
    #      EN_TIMEOFDAY     3   Control applied at specific time of day 
    # 
    # For pipes, a setting of 0 means the pipe is closed and 1 means it is open. 
    # For a pump, the setting contains the pump's speed, with 0 meaning the pump
    # is closed and 1 meaning it is open at its normal speed. 
    # For a valve, the setting refers to the valve's pressure, flow, or 
    # loss coefficient, depending on valve type.  
    #
    # For Timer or Time-of-Day controls set the nindex parameter to 0.  
    # For level controls, if the controlling node nindex is a tank then 
    # the level parameter should be a water level above the tank bottom 
    # (not an elevation). Otherwise level should be a junction pressure.  
    #
    # To remove a control on a particular link, set the lindex parameter to 0. 
    # Values for the other parameters in the function will be ignored.  
    # 
    # Example: 
    # This example uses ENgetcontrol and ENsetcontrol to change the low level
    # setting on the node that controls a link with index thelink to a new value newlevel.
    #
    # [errcode, numctrls] = ENgetcount(EN_CONTROLS)
    # for (i=1:1:numctrls)  
    #   [errcode, ctype,lindex,setting,nindex,level] = ENgetcontrol(i) 
    #   if (ctype == EN_LOWLEVEL && lindex == 1)  
    #       [errcode] = ENsetcontrol(i,ctype,lindex,setting,nindex,level)
    #   end; 
    # end;  

    errcode= _lib.ENsetcontrol(ctypes.c_int(cindex), ctypes.c_int(ctype),
                            ctypes.c_int(lindex), ctypes.c_float(setting), 
                            ctypes.c_int(nindex), ctypes.c_float(level) )
    if errcode!=0: raise ENtoolkitError(errcode)

# ============================================================================================================ 
# Retrieving other network information
# ============================================================================================================    

def ENgetcount(countcode):
    # Description: Retrieves the number of network components of a specified type.
    # Arguments:
    # countcode: component code EN_NODECOUNT
    #                          EN_TANKCOUNT
    #                          EN_LINKCOUNT
    #                          EN_PATCOUNT
    #                          EN_CURVECOUNT
    #                          EN_CONTROLCOUNT
    j= ctypes.c_int()
    errcode= _lib.ENgetcount(countcode, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENgetflowunits():
    # Description: Retrieves a code number indicating the units used to express all flow rates.
    j= ctypes.c_int()
    errcode= _lib.ENgetflowunits(ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value    

def ENgettimeparam(paramcode):
    # Description: Retrieves the value of a specific analysis time parameter.
    # Arguments:
    # paramcode: EN_DURATION     
    #            EN_HYDSTEP
    #            EN_QUALSTEP
    #            EN_PATTERNSTEP
    #            EN_PATTERNSTART
    #            EN_REPORTSTEP
    #            EN_REPORTSTART
    #            EN_RULESTEP
    #            EN_STATISTIC
    #            EN_PERIODS"""
    j= ctypes.c_int()
    errcode= _lib.ENgettimeparam(paramcode, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENgetoption(optioncode):
    # Description: Retrieves the value of a particular analysis option.
    # Arguments:
    # optioncode: EN_TRIALS       
    #            EN_ACCURACY 
    #            EN_TOLERANCE 
    #            EN_EMITEXPON 
    #            EN_DEMANDMULT
    j= ctypes.c_int()
    errcode= _lib.ENgetoption(optioncode, ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def ENgetversion():
    # Description: Retrieves the current version number of the Toolkit.
    j= ctypes.c_int()
    errcode= _lib.ENgetversion(ctypes.byref(j))
    if errcode!=0: raise ENtoolkitError(errcode)
    return j.value

def  ENsettimeparam(paramcode, timevalue):
    # Description: Sets the value of a time parameter.
    # Arguments:
    #  paramcode: time parameter code EN_DURATION
    #                                 EN_HYDSTEP
    #                                 EN_QUALSTEP
    #                                 EN_PATTERNSTEP
    #                                 EN_PATTERNSTART
    #                                 EN_REPORTSTEP
    #                                 EN_REPORTSTART
    #                                 EN_RULESTEP
    #                                 EN_STATISTIC
    #                                 EN_PERIODS
    #  timevalue: value of time parameter in seconds
    #                  The codes for EN_STATISTIC are:
    #                  EN_NONE     none
    #                  EN_AVERAGE  averaged
    #                  EN_MINIMUM  minimums
    #                  EN_MAXIMUM  maximums
    #                  EN_RANGE    ranges
    errcode= _lib.ENsettimeparam(ctypes.c_int(paramcode), ctypes.c_int(timevalue))
    if errcode!=0: raise ENtoolkitError(errcode)

def ENsetoption( optioncode, value):
    # Description: Sets the value of a particular analysis option.
    # Arguments:
    # optioncode: option code EN_TRIALS
    #                          EN_ACCURACY  
    #                          EN_TOLERANCE 
    #                          EN_EMITEXPON 
    #                          EN_DEMANDMULT
    #  value:  option value
    errcode= _lib.ENsetoption(ctypes.c_int(paramcode), ctypes.c_float(value))
    if errcode!=0: raise ENtoolkitError(errcode)
# ============================================================================================================
# Hydraulic Analysis
# ============================================================================================================

def ENsolveH():
    # Description:
    # Runs a complete hydraulic simulation with results for all time periods written to the binary Hydraulics file. 
    # Notes:
    # Use ENsolveH to generate a complete hydraulic solution which can stand alone or be 
    # used as input to a water quality analysis. It can also be followed by calls to 
    # ENsaveH and ENreport to write a report on hydraulic results to the report file. 
    # Do not use ENopenH, ENinitH, ENrunH, ENnextH, and ENcloseH in conjunction with ENsolveH.
    # Example:
    # ENopen("net1.inp", "net1.rpt", "");
    # ENsolveH();
    # ENsolveQ();
    # ENreport();
    # ENclose();
    errcode= _lib.ENsolveH()
    if errcode!=0: raise ENtoolkitError(errcode)

def ENopenH(): 
    """Opens the hydraulics analysis system"""
    errcode= _lib.ENopenH()

def ENinitH(flag=None):
    # Description:
    #  Initializes storage tank levels, link status and settings, 
    #  and the simulation clock time prior to running a hydraulic analysis. 
    # Arguments: 
    #  saveflag:  0-1 flag indicating if hydraulic results 
    #             will be saved to the hydraulics file. 
    # 
    # Notes:
    # Call ENinitH prior to running a hydraulic analysis using ENrunH and ENnextH.  
    #
    # ENopenH must have been called prior to calling ENinitH.  
    #
    # Do not call ENinitH if a complete hydraulic analysis is being made with a call to ENsolveH.  
    #
    # Set saveflag to 1 if you will be making a subsequent water quality run, 
    # using ENreport to generate a report, or using ENsavehydfile to save the binary hydraulics file.  
    errcode= _lib.ENinitH(flag)
    if errcode!=0: raise ENtoolkitError(errcode)

def ENrunH():
    # Description:
    #  Clears any report formatting commands that either appeared in the [REPORT] 
    #  section of the EPANET Input file or were issued with the ENsetreport function.  
    # Notes:
    #  After calling this function the default reporting options are in effect. These are:  
    #   · No status report  
    #   · No energy report  
    #   · No nodes reported on  
    #   · No links reported on  
    #   · Node variables reported to 2 decimal places  
    #   · Link variables reported to 2 decimal places (3 for friction factor)  
    #   · Node variables reported are elevation, head, pressure, and quality  
    #   · Link variables reported are flow, velocity, and head loss  
    errcode= _lib.ENrunH(ctypes.byref(_current_simulation_time))
    if errcode>=100: 
      raise ENtoolkitError(errcode)
    elif errcode>0:
      return ENgeterror(errcode)
    
def ENsimtime():
    # Description: retrieves the current simulation time t as datetime.timedelta instance
    return datetime.timedelta(seconds= _current_simulation_time.value )

def ENnextH():
    # Description:
    #  Determines the length of time until the next hydraulic event occurs in 
    #  an extended period simulation.   
    # 
    # Arguments: 
    # tstep:  time (in seconds) until next hydraulic event occurs or 0 if at the end of the simulation period. 
    #
    # Returns:
    #  Returns an error code.
    # 
    # Notes:
    # This function is used in conjunction with ENrunH to perform an extended 
    # period hydraulic analysis (see example below).  
    #
    # The value of tstep should be treated as a read-only variable. 
    # It is automatically computed as the smaller of:  
    #   · the time interval until the next hydraulic time step begins  
    #   · the time interval until the next reporting time step begins  
    #   · the time interval until the next change in demands occurs  
    #   · the time interval until a tank becomes full or empty  
    #   · the time interval until a control or rule fires  
    # 
    # Example: 
    #     long t, tstep;  
    #     ENopenH();  
    #     ENinitH(0);  
    #     do {  
    #      ENrunH(&t);  
    #      /* Retrieve hydraulic results for time t */  
    #      ENnextH(&tstep);  
    #     } while (tstep > 0);  
    #     ENcloseH();  
    _deltat= ctypes.c_long()
    errcode= _lib.ENnextH(ctypes.byref(_deltat))
    if errcode!=0: raise ENtoolkitError(errcode)
    return _deltat.value

def ENcloseH():
    # Description:
    # Closes the hydraulic analysis system, freeing all allocated memory.
    # Notes:
    # Call ENcloseH after all hydraulics analyses have been made using
    # ENinitH - ENrunH - ENnextH. Do not call this function if ENsolveH is being used.
    errcode= _lib.ENcloseH()
    if errcode!=0: raise ENtoolkitError(errcode)

# ============================================================================================================
# Running a quality analysis
# ============================================================================================================
 
def ENsolveQ():
    # Description: Runs a complete water quality simulation with results at uniform reporting intervals written 
    # to EPANET's binary Output file.
    errcode= _lib.ENsolveQ()
    if errcode!=0: raise ENtoolkitError(errcode)

def ENopenQ():
    # Description: Opens the water quality analysis system
    errcode= _lib.ENopenQ()

def ENinitQ(flag=None):
    # Description: Initializes water quality and the simulation clock time prior to running a water quality analysis.
    # flag  EN_NOSAVE | EN_SAVE 
    errcode= _lib.ENinitQ(flag)
    if errcode!=0: raise ENtoolkitError(errcode)

def ENrunQ():
    # Description: Makes available the hydraulic and water quality results that occur at the start of the next time period 
    # of a water quality analysis, where the start of the period is returned in t.
    errcode= _lib.ENrunQ(ctypes.byref(_current_simulation_time))
    if errcode>=100: 
      raise ENtoolkitError(errcode)
    elif errcode>0:
      return ENgeterror(errcode)

def ENnextQ():
    # Description: Advances the water quality simulation to the start of the next hydraulic time period.
    _deltat= ctypes.c_long()
    errcode= _lib.ENnextQ(ctypes.byref(_deltat))
    if errcode!=0: raise ENtoolkitError(errcode)
    return _deltat.value

def ENcloseQ():
    # Description: Closes the water quality analysis system, freeing all allocated memory.
    errcode= _lib.ENcloseQ()
    if errcode!=0: raise ENtoolkitError(errcode)
    
# ============================================================================================================

def ENsaveH():
    # Description: Transfers results of a hydraulic simulation from the binary Hydraulics file to the binary
    # Output file, where results are only reported at uniform reporting intervals.
    errcode= _lib.ENsaveH()
    if errcode!=0: raise ENtoolkitError(errcode)

def ENsaveinpfile(fname):
    # Description: Writes all current network input data to a file using the format of an EPANET input file.
    errcode= _lib.ENsaveinpfile( ctypes.c_char_p(fname))
    if errcode!=0: raise ENtoolkitError(errcode)

def ENreport():
    # Description: Writes a formatted text report on simulation results to the Report file.
    errcode= _lib.ENreport()
    if errcode!=0: raise ENtoolkitError(errcode)

def ENgeterror(errcode):
    # Description: Retrieves the text of the message associated with a particular error or warning code.
    errmsg= ctypes.create_string_buffer(_err_max_char)
    _lib.ENgeterror( errcode,ctypes.byref(errmsg), _err_max_char )
    return errmsg.value

class ENtoolkitError(Exception):
    def __init__(self, ierr):
      self.warning= ierr < 100
      self.args= (ierr,)
      self.message= ENgeterror(ierr)
      if self.message=='' and ierr!=0:
         self.message='ENtoolkit Undocumented Error '+str(ierr)+': look at text.h in epanet sources'
    def __str__(self):
      return self.message
      
# ============================================================================================================
# Parameter Glossary
# ============================================================================================================

# Node parameters
EN_ELEVATION     = 0      
EN_BASEDEMAND    = 1
EN_PATTERN       = 2
EN_EMITTER       = 3
EN_INITQUAL      = 4
EN_SOURCEQUAL    = 5
EN_SOURCEPAT     = 6
EN_SOURCETYPE    = 7
EN_TANKLEVEL     = 8
EN_DEMAND        = 9
EN_HEAD          = 10
EN_PRESSURE      = 11
EN_QUALITY       = 12
EN_SOURCEMASS    = 13
EN_INITVOLUME    = 14
EN_MIXMODEL      = 15
EN_MIXZONEVOL    = 16

EN_TANKDIAM      = 17
EN_MINVOLUME     = 18
EN_VOLCURVE      = 19
EN_MINLEVEL      = 20
EN_MAXLEVEL      = 21
EN_MIXFRACTION   = 22
EN_TANK_KBULK    = 23

# Link parameters
EN_DIAMETER      = 0      
EN_LENGTH        = 1
EN_ROUGHNESS     = 2
EN_MINORLOSS     = 3
EN_INITSTATUS    = 4
EN_INITSETTING   = 5
EN_KBULK         = 6
EN_KWALL         = 7
EN_FLOW          = 8
EN_VELOCITY      = 9
EN_HEADLOSS      = 10
EN_STATUS        = 11
EN_SETTING       = 12
EN_ENERGY        = 13

# Time parameters
EN_DURATION      = 0     
EN_HYDSTEP       = 1
EN_QUALSTEP      = 2
EN_PATTERNSTEP   = 3
EN_PATTERNSTART  = 4
EN_REPORTSTEP    = 5
EN_REPORTSTART   = 6
EN_RULESTEP      = 7
EN_STATISTIC     = 8
EN_PERIODS       = 9

# Component counts
EN_NODECOUNT     = 0      
EN_TANKCOUNT     = 1
EN_LINKCOUNT     = 2
EN_PATCOUNT      = 3
EN_CURVECOUNT    = 4
EN_CONTROLCOUNT  = 5

# Node types
EN_JUNCTION      = 0      
EN_RESERVOIR     = 1
EN_TANK          = 2

# Link types
EN_CVPIPE        = 0      
EN_PIPE          = 1
EN_PUMP          = 2
EN_PRV           = 3
EN_PSV           = 4
EN_PBV           = 5
EN_FCV           = 6
EN_TCV           = 7
EN_GPV           = 8

# Quality analysis types
EN_NONE          = 0      
EN_CHEM          = 1
EN_AGE           = 2
EN_TRACE         = 3

# Source quality types 
EN_CONCEN        = 0      
EN_MASS          = 1
EN_SETPOINT      = 2
EN_FLOWPACED     = 3

# Flow units types 
EN_CFS           = 0      
EN_GPM           = 1
EN_MGD           = 2
EN_IMGD          = 3
EN_AFD           = 4
EN_LPS           = 5
EN_LPM           = 6
EN_MLD           = 7
EN_CMH           = 8
EN_CMD           = 9

# Misc. options 
EN_TRIALS        = 0      
EN_ACCURACY      = 1
EN_TOLERANCE     = 2
EN_EMITEXPON     = 3
EN_DEMANDMULT    = 4

# Control types 
EN_LOWLEVEL      = 0      
EN_HILEVEL       = 1
EN_TIMER         = 2
EN_TIMEOFDAY     = 3

# Time statistic types. 
EN_AVERAGE       = 1      
EN_MINIMUM       = 2
EN_MAXIMUM       = 3
EN_RANGE         = 4

# Tank mixing models
EN_MIX1          = 0      
EN_MIX2          = 1
EN_FIFO          = 2
EN_LIFO          = 3

# Save-results-to-file flag 
EN_NOSAVE        = 0      
EN_SAVE          = 1
# Re-initialize flow flag  
EN_INITFLOW      = 10     

FlowUnits= { EN_CFS :"cfs"   ,
             EN_GPM :"gpm"   ,
             EN_MGD :"a-f/d" ,
             EN_IMGD:"mgd"   ,
             EN_AFD :"Imgd"  ,
             EN_LPS :"L/s"   ,
             EN_LPM :"Lpm"   ,
             EN_MLD :"m3/h"  ,
             EN_CMH :"m3/d"  ,
             EN_CMD :"ML/d"  }