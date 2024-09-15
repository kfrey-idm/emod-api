import json
import math
import numpy as np
import os
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import emod_api.demographics.grid_construction as grid
from emod_api.demographics.BaseInputFile import BaseInputFile
from emod_api.demographics.Node import Node
from emod_api.demographics.PropertiesAndAttributes import IndividualAttributes, IndividualProperty, IndividualProperties, NodeAttributes
from emod_api.demographics import DemographicsTemplates as DT
from emod_api.demographics.DemographicsInputDataParsers import node_ID_from_lat_long, duplicate_nodeID_check
from typing import List

# Just make once-static methods module-level functions


def from_template_node(lat=0, lon=0, pop=1000000, name="Erewhon", forced_id=1):
    """
    Create a single-node Demographics instance from a few params.
    """
    new_nodes = [Node(lat, lon, pop, forced_id=forced_id, name=name)]
    return Demographics(nodes=new_nodes)

# MOVE TO demographics/DemographicsInputDataParsers.py
def from_file(base_file):
    """
    Create a Demographics instance from an existing demographics file.
    """
    with open(base_file, "rb") as src:
        raw = json.load(src)
        nodes = []

        # Load the nodes
        for node in raw["Nodes"]:
            nodes.append(Node.from_data(node))

        # Load the idref
        idref = raw["Metadata"]["IdReference"]

    # Create the file
    return Demographics(nodes, idref, base_file)


def get_node_ids_from_file(demographics_file):
    """
    Get a list of node ids from a demographics file.
    """
    d = from_file(demographics_file)
    return sorted(d.node_ids)


def get_node_pops_from_params(tot_pop, num_nodes, frac_rural):
    """
    Get a list of node populations from the params used to create a sparsely 
    parameterized multi-node Demographics instance.
    """
    # Generate node sizes
    nsizes = np.exp( -np.log(np.random.rand(num_nodes - 1)))
    nsizes = frac_rural * nsizes / np.sum(nsizes)
    nsizes = np.minimum(nsizes, 100 / tot_pop)
    nsizes = frac_rural * nsizes / np.sum(nsizes)
    nsizes = np.insert(nsizes, 0, 1 - frac_rural)
    npops = ((np.round(tot_pop * nsizes, 0)).astype(int)).tolist()
    return npops


def from_params(tot_pop=1000000, num_nodes=100, frac_rural=0.3, id_ref="from_params"):
    """
    Create an EMOD-compatible Demographics object with the population and number 
    of nodes specified. frac_rural determines what fraction of the population gets
    put in the 'rural' nodes, which means all nodes besides node 1. Node 1 is the 
    'urban' node.
    """ 
    if frac_rural > 1.0:
        raise ValueError( f"frac_rural can't be greater than 1.0" )
    if frac_rural < 0.0:
        raise ValueError( f"frac_rural can't be less than 0" )
    if frac_rural == 0.0:
        frac_rural = 1e-09
    npops = get_node_pops_from_params( tot_pop, num_nodes, frac_rural )

    # Generate node lattice
    ucellb = np.array([[1.0, 0.0], [-0.5, 0.86603]])
    nlocs = np.random.rand(num_nodes, 2)
    nlocs[0, :] = 0.5
    nlocs = np.round(np.matmul(nlocs, ucellb), 4)

    nodes = []
    # Add nodes to demographics
    for idx in range(len(npops)):
        nodes.append(Node(nlocs[idx, 1], nlocs[idx, 0], npops[idx], forced_id=idx + 1))

    return Demographics(nodes=nodes, idref=id_ref)


def _create_grid_files( point_records_file_in, final_grid_files_dir, site ):
    """
    Purpose: Create grid file (as csv) from records file. 
    Author: pselvaraj
    """
    # create paths first...
    output_filename = f"{site}_grid.csv" 
    if not os.path.exists(final_grid_files_dir):
        os.mkdir(final_grid_files_dir)
    out_path = os.path.join(final_grid_files_dir, output_filename )

    if not os.path.exists( out_path ):
        # Then manip data...
        #logging.info("Reading data...")
        print( f"{out_path} not found so we are going to create it." )
        print( f"Reading {point_records_file_in}." )
        point_records = pd.read_csv(point_records_file_in, encoding="iso-8859-1")
        point_records.rename(columns={'longitude': 'lon', 'latitude': 'lat'}, inplace=True)

        if not 'pop' in point_records.columns:
            point_records['pop'] = [5.5] * len(point_records)

        if 'hh_size' in point_records.columns:
            point_records['pop'] = point_records['hh_size']

        # point_records = point_records[point_records['pop']>0]
        x_min, y_min, x_max, y_max = grid.get_bbox(point_records)
        point_records = point_records[
            (point_records.lon >= x_min) & (point_records.lon <= x_max) & (point_records.lat >= y_min) & (
                    point_records.lat <= y_max)]
        gridd, grid_id_2_cell_id, origin, final = grid.construct(x_min, y_min, x_max, y_max)
        gridd.to_csv(os.path.join(final_grid_files_dir, f"{site}_grid.csv"))

        with open(os.path.join(final_grid_files_dir, f"{site}_grid_id_2_cell_id.json"), "w") as g_f:
            json.dump(grid_id_2_cell_id, g_f, indent=3)

        point_records[['gcid', 'gidx', 'gidy']] = point_records.apply(
                grid.point_2_grid_cell_id_lookup,
                args=(grid_id_2_cell_id, origin,), axis=1).apply(pd.Series)

        grid_pop = point_records.groupby(['gcid', 'gidx', 'gidy'])['pop'].apply(np.sum).reset_index()
        grid_pop['pop'] = grid_pop['pop'].apply(lambda x: round(x/5))
        grid_final = pd.merge(gridd, grid_pop, on='gcid')
        grid_final['node_label'] = list(grid_final.index)
        grid_final = grid_final[grid_final['pop'] > 5]
        grid_final.to_csv(os.path.join(final_grid_files_dir, output_filename ))

    print( f"{out_path} gridded population file created or found." )
    return out_path 

def from_csv(input_file, res=30/3600, id_ref="from_csv"):
    """
    Create an EMOD-compatible Demographics instance from a csv population-by-node file.
    """
    def get_value(row, headers):
        for h in headers:
            if row.get(h) is not None:
                return float(row.get(h))
        return None

    if not os.path.exists(input_file):
        print(f"{input_file} not found.")
        return

    print( f"{input_file} found and being read for demographics.json file creation." )
    node_info = pd.read_csv(input_file, encoding='iso-8859-1')
    out_nodes = []
    for index, row in node_info.iterrows():
        pop = 0
        if 'under5_pop' in row:
            pop = int(6*row['under5_pop'])
            if pop<25000:
                continue
        else:
            pop = int(row['pop'])

        latitude_headers = ["lat", "latitude", "LAT", "LATITUDE", "Latitude", "Lat"]
        lat = get_value(row, latitude_headers)

        longitude_headers = ["lon", "longitude", "LON", "LONGITUDE", "Longitude", "Lon"]
        lon = get_value(row, longitude_headers)

        birth_rate_headers = ["birth", "Birth", "birth_rate", "birthrate", "BirthRate", "Birth_Rate", "BIRTH", "birth rate", "Birth Rate"]
        birth_rate = get_value(row, birth_rate_headers)
        if birth_rate is not None and birth_rate < 0.0:
            raise ValueError("Birth rate defined in " + input_file + " must be greater 0.")

        node_id = row.get('node_id')
        if node_id is not None and int(node_id) == 0:
            raise ValueError( "Node ids can not be '0'." )

        forced_id = int(node_id) if (node_id is not None) else int(node_ID_from_lat_long(lat, lon, res))

        place_name = ""
        if 'loc' in row:
            place_name = str(row['loc'])
        meta = {} 
        """
        meta = {'dot_name': (row['ADM0_NAME']+':'+row['ADM1_NAME']+':'+row['ADM2_NAME']),
                'GUID': row['GUID'],
                'density': row['under5_pop_weighted_density']}
        """
        node_attributes = NodeAttributes(name=place_name, birth_rate=birth_rate)
        node = Node(lat, lon, pop,
                    node_attributes=node_attributes,
                    forced_id=forced_id, meta=meta)

        out_nodes.append(node)
    out_nodes = duplicate_nodeID_check(out_nodes)
    for node in out_nodes:
        if node.id == 1639001798:  #Not sure why this node causes issues, just dump it for speed.  Probably an issue in the duplicate nodeID check
            remel = node
            out_nodes.remove(remel)

    return Demographics(nodes=out_nodes, idref=id_ref)

def from_pop_csv( pop_filename_in, pop_filename_out="spatial_gridded_pop_dir", site="No_Site" ):
    # This should be a 'raw' ungridded file that needs to be converted into a pop_grid using _create_grid_files from household lat-lons
    # Don't do this if the grid file already exists.
    grid_file_path = _create_grid_files( pop_filename_in, pop_filename_out, site )
    print( f"{grid_file_path} grid file created." )
    return from_csv( grid_file_path )

class Demographics(BaseInputFile):
    """
    This class is a container of data necessary to produce a EMOD-valid demographics input file. It can be initialized from 
    an existing valid demographics.joson type file or from an array of valid Nodes.
    """
    def __init__(self, nodes, idref="Gridded world grump2.5arcmin", base_file=None):
        """
        A class to create demographics.
        :param nodes: list of Nodes
        :param idref: A name/reference
        :param base_file: A demographics file in json format
        """
        super(Demographics, self).__init__(idref) 
        self._nodes = nodes
        self.idref = idref
        self.raw = None
        self.implicits = list()

        if base_file:
            with open(base_file, "rb") as src:
                self.raw = json.load(src)
        else:
            meta = self.generate_headers()
            self.raw = {"Metadata": meta, "Defaults": {}}

            self.SetMinimalNodeAttributes()

            self.raw["Defaults"]["IndividualAttributes"] = {}
            # Uniform prevalence between .1 and .3
            #self.raw["Defaults"]["IndividualAttributes"].update( DT.InitPrevUniform() )
            #self.raw["Defaults"]["IndividualAttributes"].update( DT.InitSusceptConstant() )
            self.raw["Defaults"]["IndividualAttributes"].update( DT.NoRisk() )
            #self.raw["Defaults"]["IndividualAttributes"].update( DT.InitAgeUniform() )
            DT.NoInitialPrevalence(self) # does this need to be called?
            #DT.InitSusceptConstant(self) # move this to Measles and maybe other subclasses
            #DT.NoRisk()
            self.raw["Defaults"]["IndividualProperties"] = []
            DT.InitAgeUniform(self)

    def apply_overlay(self, overlay_nodes: list):
        """
        :param overlay_nodes: Overlay list of nodes over existing nodes in demographics
        :return:
        """
        map_ids_overlay = {}    # map node_id to overlay node_id
        for node in overlay_nodes:
            map_ids_overlay[node.forced_id] = node

        for index, node in enumerate(self.nodes):
            if map_ids_overlay.get(node.forced_id):
                self.nodes[index].update(map_ids_overlay[node.forced_id])

    def to_dict(self):
        self.raw["Nodes"] = []

        for node in self._nodes:
            d = node.to_dict()
            d.update(node.meta)
            self.raw["Nodes"].append(d)

        # Update node count
        self.raw["Metadata"]["NodeCount"] = len(self._nodes)
        return self.raw

    def generate_file(self, name="demographics.json"):
        """
        Write the contents of the instance to an EMOD-compatible (JSON) file.
        """
        with open(name, "w") as output:
            json.dump(self.to_dict(), output, indent=3, sort_keys=True)

        return name

    @property
    def node_ids(self):
        """
        Return the list of (geographic) node ids.
        """
        return [node.to_dict()["NodeID"] for node in self._nodes]

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, values):
        self._nodes = values

    @property
    def node_count(self):
        """
        Return the number of (geographic) nodes.
        """
        return len(self._nodes)

    def get_node(self, nodeid):
        """
        Return the node idendified by nodeid. Search either name or actual id
        :param nodeid: 
        :return: 
        """
        for node in self._nodes:
            if node.id == nodeid or node.name == nodeid:
                return node
        raise ValueError(
            "No nodes available with the id: %s. Available nodes (%s)"
            % (nodeid, ", ".join([str(node.name) for node in self._nodes]))
        )

    def SetIndividualAttributesWithFertMort(self, CrudeBirthRate=40/1000, CrudeMortRate = 20/1000):
        self.raw['Defaults']['IndividualAttributes'] = {}
        DT.NoInitialPrevalence( self )
        # self.raw['Defaults']['IndividualAttributes'].update(DT.NoRiskHeterogeneity())

        #Alternative to EveryoneInitiallySusceptible is SimpleSusceptibilityDistribution(meanAgeAtInfection=2.5 or some other number)
        DT.EveryoneInitiallySusceptible( self )
        self.SetMortalityRate(CrudeMortRate)
        self.SetEquilibriumAgeDistFromBirthAndMortRates(CrudeBirthRate, CrudeMortRate)

    def AddIndividualPropertyAndHINT(self, Property: str, Values: List[str], InitialDistribution:List[float] = None,
                                     TransmissionMatrix:List[List[float]] = None, Transitions: List=None):
        """
        Add Individual Properties, including an optional HINT configuration matrix.

        Args:
            Property: property (if property already exists an exception is raised).
            Values: property values.
            InitialDistribution: initial distribution.
            TransmissionMatrix: transmission matrix.

        Returns:
            N/A/
        """
        if 'IndividualProperties' not in self.raw['Defaults']:
            self.raw['Defaults']['IndividualProperties'] = []
        if any([Property == x['Property'] for x in self.raw['Defaults']['IndividualProperties']]):
            raise ValueError("Property Type '{0}' already present in IndividualProperties list".format(Property))
        else:
            # Check if Property is in whitelist. If not, auto-set Disable_IP_Whitelist
            iplist = ["Age_Bin", "Accessibility", "Geographic", "Place", "Risk", "QualityOfCare", "HasActiveTB", "InterventionStatus"]
            if Property not in iplist:
                # print("Need to set Disable_IP_Whitelist in config.")
                def update_config( config ):
                    config.parameters["Disable_IP_Whitelist"] = 1
                    return config
                if self.implicits is not None:
                    self.implicits.append( update_config )

            transmission_matrix = None
            if TransmissionMatrix is not None:
                transmission_matrix = {"Route": "Contact",
                                       "Matrix": TransmissionMatrix}

            individual_property = IndividualProperty(property=Property,
                                                     values=Values,
                                                     initial_distribution=InitialDistribution,
                                                     transitions=Transitions,
                                                     transmission_matrix=transmission_matrix)
            self.raw['Defaults']['IndividualProperties'].append(individual_property.to_dict())

        if TransmissionMatrix is not None:
            def update_config(config):
                config.parameters.Enable_Heterogeneous_Intranode_Transmission = 1
                return config

            if self.implicits is not None:
                self.implicits.append(update_config)

    def AddAgeDependentTransmission(
            self,
            Age_Bin_Edges_In_Years = [0, 1, 2, -1],
            TransmissionMatrix = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]):
        """
        Set up age-based HINT. Since ages are a first class property of an agent, Age_Bin is a special case
        of HINT. We don't specify a distribution, but we do specify the age bin edges, in units of years.
        So if Age_Bin_Edges_In_Years = [ 0, 10, 65, -1 ] it means you'll have 3 age buckets: 0-10, 10-65, & 65+.
        Always 'book-end' with 0 and -1.

        Args:
            Age_Bin_Edges_In_Years: array (or list) of floating point values, representing the age bucket bounderies.
            TransmissionMatrix: 2-D array of floating point values, representing epi connectedness of the age buckets.

        """

        if Age_Bin_Edges_In_Years[0] != 0:
            raise ValueError( "First value of 'Age_Bin_Edges_In_Years' must be 0." )
        if Age_Bin_Edges_In_Years[-1] != -1:
            raise ValueError( "Last value of 'Age_Bin_Edges_In_Years' must be -1." )
        num_age_buckets = len(Age_Bin_Edges_In_Years)-1
        if len(TransmissionMatrix) != num_age_buckets:
            raise ValueError( f"Number of rows of TransmissionMatrix ({len(TransmissionMatrix)}) must match number of age buckets ({num_age_buckets})." )
        for idx in range(len(TransmissionMatrix)):
            num_cols = len(TransmissionMatrix[idx])
            if num_cols != num_age_buckets:
                raise ValueError( f"Number of columns of TransmissionMatrix ({len(TransmissionMatrix[idx])}) must match number of age buckets ({num_age_buckets})." )

        self.AddIndividualPropertyAndHINT("Age_Bin", Age_Bin_Edges_In_Years, None, TransmissionMatrix)
        def update_config(config):
            config.parameters.Enable_Heterogeneous_Intranode_Transmission = 1
            return config

        if self.implicits is not None:
            self.implicits.append(update_config)

    def SetDefaultIndividualAttributes(self): 
        """
        NOTE: This is very Measles-ish. We might want to move into MeaslesDemographics
        """
        self.raw['Defaults']['IndividualAttributes'] = {}
        DT.NoInitialPrevalence(self)
        #Age distribution from UNWPP
        DT.AgeStructureUNWPP(self)
        #Mortality rates carried over from Nigeria DHS
        DT.MortalityStructureNigeriaDHS(self)
        DT.DefaultSusceptibilityDistribution(self)

    def SetMinimalNodeAttributes(self): 
        self.SetDefaultNodeAttributes(birth=False)

    def SetBirthRate(self, birth_rate):
        """
        Set Default birth rate to birth_rate. Turn on Vital Dynamics and Births implicitly.
        """
        self.raw['Defaults']['NodeAttributes'].update({
            "BirthRate": birth_rate
        })
        self.implicits.append(DT._set_enable_births)

    def SetMortalityRate(self, mortality_rate, node_ids: List[int] = None):
        """
        Set constant mortality rate to mort_rate. Turn on Enable_Natural_Mortality implicitly.
        """
        if node_ids is None:
            setting = {"MortalityDistribution": DT._ConstantMortality(mortality_rate).to_dict()}
            self.SetDefaultFromTemplate(setting)
        else:
            for node_id in node_ids:
                distribution = DT._ConstantMortality(mortality_rate)
                self.get_node(node_id)._set_mortality_distribution(distribution)

        if self.implicits is not None:
            self.implicits.append(DT._set_mortality_age_gender)

    def SetMortalityDistribution(self, distribution: IndividualAttributes.MortalityDistribution = None, node_ids: List[int] = None):
        """
        Set a default mortality distribution for all nodes or per node. Turn on Enable_Natural_Mortality implicitly.
        Args:
            distribution: distribution
            node_ids: a list of node_ids

        Returns:
            None
        """
        if node_ids is None:
            self.raw["Defaults"]["IndividualAttributes"]["MortalityDistribution"] = distribution.to_dict()
        else:
            for node_id in node_ids:
                self.get_node(node_id)._set_mortality_distribution(distribution)

        if self.implicits is not None:
            self.implicits.append(DT._set_mortality_age_gender)

    def SetAgeDistribution(self, distribution: IndividualAttributes.AgeDistribution, node_ids: List[int] = None):
        """
        Set a default age distribution for all nodes or per node. Sets distribution type to COMPLEX implicitly.
        Args:
            distribution: age distribution
            node_ids: a list of node_ids

        Returns:
            None
        """
        if node_ids is None:
            self.raw["Defaults"]["IndividualAttributes"]["AgeDistribution"] = distribution.to_dict()
        else:
            for node_id in node_ids:
                self.get_node(node_id)._set_age_distribution(distribution)

        if self.implicits is not None:
            self.implicits.append(DT._set_age_complex)

    def SetDefaultNodeAttributes(self, birth=True):
        """
        Set the default NodeAttributes (Altitude, Airport, Region, Seaport), optionally including birth, 
        which is most important actually.
        """
        self.raw['Defaults']['NodeAttributes'] = {
                    "Altitude": 0,
                    "Airport": 1, # why are these still needed?
                    "Region": 1,
                    "Seaport": 1
                    }
        if birth:
            self.SetBirthRate( math.log(1.03567)/365 )

    def SetDefaultIndividualProperties(self):
        """
        Initialize Individual Properties to empty.
        """
        self.raw['Defaults']['IndividualProperties'] = []

    def SetDefaultProperties(self): 
        """
        Set a bunch of defaults (age structure, initial susceptibility and initial prevalencec) to sensible values.
        """
        self.SetDefaultNodeAttributes()
        self.SetDefaultIndividualAttributes() #Distributions for initialization of immunity, risk heterogeneity, etc.
        self.SetDefaultIndividualProperties() #Individual properties like accessibility, for targeting interventions

    def SetDefaultPropertiesFertMort(self, CrudeBirthRate = 40/1000, CrudeMortRate = 20/1000):
        """
        Set a bunch of defaults (birth rates, death rates, age structure, initial susceptibility and initial prevalencec) to sensible values.
        """
        self.SetDefaultNodeAttributes() 
        self.SetDefaultIndividualAttributes() #Distributions for initialization of immunity, risk heterogeneity, etc.
        self.SetBirthRate(CrudeBirthRate)
        self.SetMortalityRate(CrudeMortRate)
        #self.SetDefaultIndividualProperties() #Individual properties like accessibility, for targeting interventions

    def SetDefaultFromTemplate(self, template, setter_fn=None):
        """
        Add to the default IndividualAttributes using the input template (raw json) and set corresponding 
        config values per the setter_fn. The template should always be constructed by a 
        function in DemographicsTemplates. Eventually this function will be hidden and only 
        accessed via separate application-specific API functions such as the ones below.
        """
        # TBD: Add some error checking. Make sure IndividualAttributes are Individual, not individual.
        self.raw['Defaults']['IndividualAttributes'].update(template)
        if self.implicits is not None and setter_fn is not None:
            self.implicits.append(setter_fn)

    def SetNodeDefaultFromTemplate(self, template, setter_fn):
        """
        Add to the default NodeAttributes using the input template (raw json) and set 
        corresponding config values per the setter_fn. The template should always 
        be constructed by a function in DemographicsTemplates. Eventually this function 
        will be hidden and only accessed via separate application-specific API functions 
        such as the ones below.
        """
        # TBD: Add some error checking. Make sure NodeAttributes are Node, not individual.
        self.raw['Defaults']['NodeAttributes'].update(template)
        if self.implicits is not None:
            self.implicits.append(setter_fn)

    def SetEquilibriumAgeDistFromBirthAndMortRates( self, CrudeBirthRate=40/1000, CrudeMortRate=20/1000 ):
        """
        Set the inital ages of the population to a sensible equilibrium profile based on the specified input birth and death rates. Note this does not set the fertility and mortality rates.
        """
        self.SetDefaultFromTemplate( DT._EquilibriumAgeDistFromBirthAndMortRates(CrudeBirthRate,CrudeMortRate), DT._set_age_complex )

    def SetInitialAgeExponential(self, rate=0.0001068, description=""):
        """
        Set the initial age of the population to an exponential distribution with a specified rate.
        :param  rate: rate
        :param  description: description, why was this distribution chosen
        """
        if not description:
            description = "Initial ages set to draw from exponential distribution with {rate}"

        setting = {"AgeDistributionFlag": 3,
                   "AgeDistribution1": rate,
                   "AgeDistribution2": 0,
                   "AgeDistribution_Description": description}
        self.SetDefaultFromTemplate( setting, DT._set_age_simple )

    def SetInitialAgeLikeSubSaharanAfrica( self, description="" ):
        """
        Set the initial age of the population to a overly simplified structure that sort of looks like 
        sub-Saharan Africa. This uses the SetInitialAgeExponential.
        :param  description: description, why was this age chosen?
        """
        if not description:
            description = f"Setting initial age distribution like Sub Saharan Africa, drawing from exponential distribution."

        self.SetInitialAgeExponential(description=description) # use default rate

    def SetOverdispersion( self, new_overdispersion_value, nodes=[] ):
        """
        Set the overdispersion value for the specified nodes (all if empty).
        """
        def enable_overdispersion( config ):
            print( "DEBUG: Setting 'Enable_Infection_Rate_Overdispersion' to 1." )
            config.parameters.Enable_Infection_Rate_Overdispersion = 1
            return config
        if self.implicits is not None:
            self.implicits.append( enable_overdispersion )
        self.raw['Defaults']['NodeAttributes']["InfectivityOverdispersion"] = new_overdispersion_value

    def SetConstantSusceptibility( self ):
        """
        Set the initial susceptibilty for each new individual to a constant value of 1.0.
        """
        DT.InitSusceptConstant(self)

    def SetInitPrevFromUniformDraw( self, min_init_prev, max_init_prev, description="" ):
        """
        Set Initial Prevalence (one value per node) drawn from an uniform distribution.
        :param  min_init_prev: minimal initial prevalence
        :param  max_init_prevalence: maximal initial prevalence
        :param  description: description, why were these parameters chosen?
        """
        if not description:
            description = f"Drawing prevalence from uniform distribution, min={min_init_prev} and max={max_init_prev}"

        DT.InitPrevUniform( self, min_init_prev, max_init_prev, description )

    def SetConstantRisk( self, risk=1, description="" ):
        """
        Set the initial risk for each new individual to the same value, defaults to full risk
        :param  risk: risk
        :param  description: description, why was this parameter chosen?
        """
        if not description:
            description = f"Risk is set to constant, risk={risk}"

        if risk == 1:
            DT.FullRisk( self, description )
        else:
            # Could add a DT.ConstantRisk but I like using less code.
            DT.InitRiskUniform( self, risk, risk, description )

    def SetHeteroRiskUniformDist( self, min_risk=0, max_risk=1 ):
        """
        Set the initial risk for each new individual to a value drawn from a uniform distribution.
        """
        DT.InitRiskUniform( self, min_lim=min_risk, max_lim=max_risk)

    def SetHeteroRiskLognormalDist( self, mean=1.0, sigma=0 ):
        """
        Set the initial risk for each new individual to a value drawn from a log-normal distribution.
        """
        DT.InitRiskLogNormal( self, mean=mean, sigma=sigma)

    def SetHeteroRiskExponDist( self, mean=1.0 ):
        """
        Set the initial risk for each new individual to a value drawn from an exponential distribution.
        """
        DT.InitRiskExponential( self, mean=mean )

    def _SetInfectivityMultiplierByNode( self, node_id_to_multplier ):
        raise ValueError( "Not Yet Implemented." )

    def infer_natural_mortality(
            self,
            file_male,
            file_female,
            interval_fit=[1970, 1980],
            which_point='mid',
            predict_horizon=2050,
            csv_out=False,
            n=0, # I don't know what this means
            results_scale_factor=1.0/365.0):
        """
        Calculate and set the expected natural mortality by age, sex, and year from data, predicting what it would
        have been without disease (usually HIV).
        """
        from collections import OrderedDict
        from sklearn.linear_model import LinearRegression
        from functools import reduce

        name_conversion_dict = {'Age (x)': 'Age',
                                'Central death rate m(x,n)': 'Mortality_mid',
                                'Age interval (n)': 'Interval',
                                'Period': 'Years'
                                }
        sex_dict = {'Male': 0, 'Female': 1}

        def construct_interval(x, y):
            return (x, x + y)

        def midpoint(x, y):
            return (x + y) / 2.0

        def generate_dict_order(tuple_list, which_entry=1):
            my_unordered_list = tuple_list.apply(lambda x: x[which_entry])
            dict_to_order = OrderedDict(zip(tuple_list, my_unordered_list))
            return dict_to_order

        def map_year(x_tuple, flag='mid'):
            valid_entries_loc = ['mid', 'end', 'start']

            if flag not in valid_entries_loc:
                raise ValueError('invalid endpoint specified')

            if flag == 'mid':
                return (x_tuple[0] + x_tuple[1]) / 2.0
            elif flag == 'start':
                return x_tuple[0]
            else:
                return x_tuple[1]

        import pandas as pd
        import numpy as np
        df_mort_male = pd.read_csv(file_male, usecols=name_conversion_dict)
        df_mort_male['Sex'] = 'Male'
        df_mort_female = pd.read_csv(file_female, usecols=name_conversion_dict)
        df_mort_female['Sex'] = 'Female'
        df_mort = pd.concat([df_mort_male, df_mort_female], axis=0)
        df_mort.rename(columns=name_conversion_dict, inplace=True)
        df_mort['Years'] = df_mort['Years'].apply(lambda xx: tuple(
            [float(zz) for zz in xx.split('-')]))  # this might be a bit too format specific (ie dashes in input)

        # log transform the data and drop unneeded columns
        df_mort['log_Mortality_mid'] = df_mort['Mortality_mid'].apply(lambda x: np.log(x))
        df_mort['Age'] = df_mort[['Age', 'Interval']].apply(lambda zz: construct_interval(*zz), axis=1)

        year_order_dict = generate_dict_order(df_mort['Years'])
        age_order_dict = generate_dict_order(df_mort['Age'])
        df_mort['sortby2'] = df_mort['Age'].map(age_order_dict)
        df_mort['sortby1'] = df_mort['Sex'].map(sex_dict)
        df_mort['sortby3'] = df_mort['Years'].map(year_order_dict)
        df_mort.sort_values(['sortby1', 'sortby2', 'sortby3'], inplace=True)
        df_mort.drop(columns=['Mortality_mid', 'Interval', 'sortby1', 'sortby2', 'sortby3'], inplace=True)

        # convert to years (and to string for age_list due to really annoying practical slicing reasons
        df_mort['Years'] = df_mort['Years'].apply(lambda x: map_year(x, which_point))
        df_mort['Age'] = df_mort['Age'].apply(lambda x: str(x))
        df_before_time = df_mort[df_mort['Years'].between(0, interval_fit[0])].copy()

        df_mort.set_index(['Sex', 'Age'], inplace=True)
        sex_list = list(set(df_mort.index.get_level_values('Sex')))
        age_list = list(set(df_mort.index.get_level_values('Age')))

        df_list = []
        df_list_future = []
        for sex in sex_list:
            for age in age_list:
                tmp_data = df_mort.loc[(sex, age, slice(None)), :]
                extrap_model = make_pipeline(StandardScaler(with_mean=False), LinearRegression())

                first_extrap_df = tmp_data[tmp_data['Years'].between(interval_fit[0], interval_fit[1])]
                XX = tmp_data[tmp_data['Years'].between(interval_fit[0], predict_horizon)].values[:, 0]

                values = first_extrap_df.values
                extrap_model.fit(values[:, 0].reshape(-1, 1), values[:, 1])

                extrap_predictions = extrap_model.predict(XX.reshape(-1, 1))

                loc_df = pd.DataFrame.from_dict({'Sex': sex, 'Age': age, 'Years': XX, 'Extrap': extrap_predictions})
                loc_df.set_index(['Sex', 'Age', 'Years'], inplace=True)

                df_list.append(loc_df.copy())

        df_e1 = pd.concat(df_list, axis=0)

        df_list_final = [df_mort, df_e1]
        df_total = reduce(lambda left, right: pd.merge(left, right, on=['Sex', 'Age', 'Years']), df_list_final)

        df_total = df_total.reset_index(inplace=False).set_index(['Sex', 'Age'], inplace=False)

        df_total['Extrap'] = df_total['Extrap'].apply(np.exp)
        df_total['Data'] = df_total['log_Mortality_mid'].apply(np.exp)
        df_before_time['Data'] = df_before_time['log_Mortality_mid'].apply(np.exp)

        df_before_time.set_index(['Sex', 'Age'], inplace=True)
        df_total = pd.concat([df_total, df_before_time], axis=0, join='outer', sort=True)

        df_total.reset_index(inplace=True)
        df_total['sortby2'] = df_total['Age'].map(age_order_dict)
        df_total['sortby1'] = df_total['Sex'].map(sex_dict)
        df_total.sort_values(by=['sortby1', 'sortby2', 'Years'], inplace=True)
        df_total.drop(columns=['sortby1', 'sortby2'], inplace=True)

        estimates_list = []
        estimates_list.append(df_total.copy()) 
        #estimates_list = [df_total.copy()] alternative
       
        def min_not_nan(x_list):
            loc_in = list(filter(lambda x: not np.isnan(x), x_list))
            return np.min(loc_in)

        # This was in another function before
        df = estimates_list[n]
        df['FE'] = df[['Data', 'Extrap']].apply(min_not_nan, axis=1)
        df['Age'] = df['Age'].apply(lambda x: int(x.split(',')[1].split(')')[0]))
        male_df = df[df['Sex'] == 'Male']
        female_df = df[df['Sex'] == 'Female']

        male_df.set_index(['Sex','Age', 'Years'], inplace=True)
        female_df.set_index(['Sex','Age','Years'], inplace=True)
        male_data = male_df['FE']
        female_data = female_df['FE']

        male_data = male_data.unstack(-1)
        male_data.sort_index(level ='Age', inplace=True)
        female_data = female_data.unstack(-1)
        female_data.sort_index(level='Age', inplace=True)

        years_out_male = list(male_data.columns)
        years_out_female =list( female_data.columns)

        age_out_male = list(male_data.index.get_level_values('Age'))
        age_out_female = list(male_data.index.get_level_values('Age'))

        male_output= male_data.values
        female_output = female_data.values

        if csv_out:
            male_data.to_csv(f'Male{csv_out}')
            female_data.to_csv(f'Female{csv_out}')

        # TBD: This is the part that should use base file functionality
        
        dict_female = {'NumPopulationGroups': list(female_data.shape),
                       'AxisNames': ['age', 'year'],
                       'AxisScaleFactors': [365.0, 1],
                       'AxisUnits': ['years', 'years'],
                       'NumDistributionAxes': 2,
                       'PopulationGroups': [age_out_female, years_out_female],
                       'ResultScaleFactor': results_scale_factor,
                       'ResultUnits': 'annual deaths per capita',
                       'ResultValues': female_output.tolist()
                       }

        dict_male =   {'NumPopulationGroups': list(male_data.shape),
                       'AxisNames': ['age', 'year'],
                       'AxisScaleFactors': [365.0, 1],
                       'AxisUnits': ['years', 'years'],
                       'NumDistributionAxes': 2,
                       'PopulationGroups': [age_out_male, years_out_male],
                       'ResultScaleFactor': results_scale_factor,
                       'ResultUnits': 'annual deaths per capita',
                       'ResultValues': male_output.tolist()
                       }
        male_mort = { "MortalityDistributionMale" : dict_male }
        female_mort = { "MortalityDistributionFemale" : dict_female }
        self.SetDefaultFromTemplate( male_mort, DT._set_mortality_age_gender_year )
        self.SetDefaultFromTemplate( female_mort )


class DemographicsOverlay:
    def __init__(self, nodes=None, meta_data: dict = None,
                 individual_attributes=None,
                 node_attributes=None,
                 mortality_distribution=None):
        self.nodes = nodes
        self.individual_attributes = individual_attributes
        self.node_attributes = node_attributes
        self.meta_data = meta_data
        self.mortality_distribution = mortality_distribution

    def to_dict(self):
        assert self.nodes

        out = {"Defaults": {}}
        if self.individual_attributes:
            out["Defaults"]["IndividualAttributes"] = self.individual_attributes.to_dict()

        if self.node_attributes:
            out["Defaults"]["NodeAttributes"] = self.node_attributes.to_dict()

        if self.meta_data:
            out["Metadata"] = self.meta_data    # there is no metadata class

        nodes_list = []
        for n in self.nodes:
            nodes_list.append({"NodeID": n})
        out["Nodes"] = nodes_list

        return out

    def to_file(self, file_name="demographics_overlay.json"):
        with open(file_name, "w") as demo_override_f:
            json.dump(self.to_dict(), demo_override_f, indent=4)
