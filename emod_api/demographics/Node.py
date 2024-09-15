import json
import math
from emod_api.demographics.Updateable import Updateable
from emod_api.demographics.PropertiesAndAttributes import IndividualAttributes, IndividualProperty, IndividualProperties, NodeAttributes


class Node(Updateable):
    default_population = 1000
    res_in_degrees = 2.5 / 60

    def __init__(
            self,
            lat,
            lon,
            pop,
            name: str = None,
            area: float = None,
            forced_id: int = None,
            individual_attributes: IndividualAttributes = None,
            individual_properties: IndividualProperties = None,
            node_attributes: NodeAttributes = None,
            meta: dict = None
    ):
        """
        Represent a Node
        :param lat: Latitude
        :param lon: Longitude
        :param pop: Population
        :param name:  Facility name
        :param area:  Area
        :param forced_id: Do we want a custom id instead of the normal ID based on lat/lon?
        """
        super().__init__()
        self.name = name
        self.forced_id = forced_id
        self.meta = meta if meta else {}
        self.individual_attributes = individual_attributes if individual_attributes else IndividualAttributes()
        self.individual_properties = individual_properties if individual_properties else IndividualProperties()
        self.node_attributes = NodeAttributes(latitude=lat, longitude=lon, initial_population=pop, name=name, area=area)
        if node_attributes is not None:
            self.node_attributes.update(node_attributes)

    def __repr__(self):
        return f"{self.node_attributes.name} - ({self.node_attributes.latitude},{self.node_attributes.longitude})"

    def to_dict(self) -> dict:
        if self.name:
            self.node_attributes.name = self.name

        d = {"NodeID": self.id,
             "NodeAttributes": self.node_attributes.to_dict()}

        if self.individual_attributes:
            d["IndividualAttributes"] = self.individual_attributes.to_dict()

        if self.individual_properties:
            ip_dict = {"IndividualProperties": []}
            for ip in self.individual_properties:
                ip_dict["IndividualProperties"].append(ip.to_dict())
            d.update(ip_dict)
        return d

    def to_tuple(self):
        return self.node_attributes.latitude, self.node_attributes.longitude, self.node_attributes.initial_population

    @property
    def id(self):
        return (
            self.forced_id
            if self.forced_id is not None
            else nodeid_from_lat_lon(self.node_attributes.latitude, self.node_attributes.longitude, self.res_in_degrees)
        )

    @classmethod
    def init_resolution_from_file(cls, fn):
        if "30arcsec" in fn:
            cls.res_in_degrees = 30 / 3600.0
        elif "2_5arcmin" in fn:
            cls.res_in_degrees = 2.5 / 30
        else:
            raise Exception("Don't recognize resolution from demographics filename")

    @classmethod
    def from_data(cls, data: dict):
        """
        Function used to create the node object from data (most likely coming from a demographics file)
        :param data: 
        :return: 
        """
        nodeid = data["NodeID"]
        node_attributes_dict = dict(data.get("NodeAttributes"))
        attributes = data["NodeAttributes"]
        latitude = attributes.pop("Latitude")
        longitude = attributes.pop("Longitude")
        population = attributes.pop("InitialPopulation", Node.default_population)
        name = attributes.pop("FacilityName", nodeid)
        individual_attributes_dict = data.get("IndividualAttributes")
        individual_properties_dict = data.get("IndividualProperties")

        individual_properties = IndividualProperties()
        if individual_properties_dict:
            if type(individual_properties_dict) is dict:
                individual_properties.append(individual_properties_dict)
            if type(individual_properties_dict) is list:
                for ip in individual_properties_dict:
                    individual_properties.add(IndividualProperty(property=ip["Property"],
                                                                           values=ip["Values"],
                                                                           transitions=ip["Transitions"],
                                                                           initial_distribution=ip["Initial_Distribution"]))
        individual_attributes = None
        if individual_attributes_dict:
            individual_attributes = IndividualAttributes().from_dict(individual_attributes_dict)

        node_attributes = None
        if node_attributes_dict:
            node_attributes = NodeAttributes().from_dict(node_attributes_dict)

        # Create the node
        cls.node = Node(node_attributes.latitude, node_attributes.longitude, node_attributes.initial_population,
                        name=name, forced_id=nodeid, individual_attributes=individual_attributes,
                        individual_properties=individual_properties, node_attributes=node_attributes)
        return cls.node

    @property
    def pop(self):
        return self.node_attributes.initial_population

    @pop.setter
    def pop(self, value):
        self.node_attributes.initial_population = value

    @property
    def lon(self):
        return self.node_attributes.longitude

    @lon.setter
    def lon(self, value):
        self.node_attributes.longitude = value

    @property
    def lat(self):
        return self.node_attributes.latitude

    @lat.setter
    def lat(self, value):
        self.node_attributes.latitude = value

    @property
    def birth_rate(self):
        return self.node_attributes.birth_rate

    @birth_rate.setter
    def birth_rate(self, value):
        self.node_attributes.birth_rate = value

    def _set_individual_attributes(self, ind_attribute: IndividualAttributes):
        self.individual_attributes = ind_attribute

    def _set_individual_properties(self, ind_properties: IndividualProperties):
        self.individual_properties = ind_properties

    def _add_individual_property(self, ind_property: IndividualProperty):
        self.individual_properties.add(ind_property)

    def _set_node_attributes(self, node_attributes: NodeAttributes):
        self.node_attributes = node_attributes

    def _set_mortality_distribution(self, distribution: IndividualAttributes.MortalityDistribution = None):
        self.individual_attributes.mortality_distribution = distribution

    def _set_age_distribution(self, distribution: IndividualAttributes.AgeDistribution = None):
        self.individual_attributes.age_distribution = distribution


class OverlayNode(Node):
    """
    Node that only requires an ID. Use to overlay a Node.
    """

    def __init__(self,
                 node_id,
                 latitude=None,
                 longitude=None,
                 initial_population=None,
                 **kwargs
                 ):
        super(OverlayNode, self).__init__(latitude, longitude, initial_population,
                                          forced_id=node_id,
                                          **kwargs
                                          )


def get_xpix_ypix(nodeid):
    ypix = (nodeid - 1) & 2 ** 16 - 1
    xpix = (nodeid - 1) >> 16
    return (xpix, ypix)


def lat_lon_from_nodeid(nodeid, res_in_deg=Node.res_in_degrees):
    xpix, ypix = get_xpix_ypix(nodeid)
    lat = (0.5 + ypix) * res_in_deg - 90.0
    lon = (0.5 + xpix) * res_in_deg - 180.0
    return (lat, lon)


def xpix_ypix_from_lat_lon(lat, lon, res_in_deg=Node.res_in_degrees):
    xpix = int(math.floor((lon + 180.0) / res_in_deg))
    ypix = int(math.floor((lat + 90.0) / res_in_deg))
    return xpix, ypix


def nodeid_from_lat_lon(lat, lon, res_in_deg=Node.res_in_degrees):
    xpix, ypix = xpix_ypix_from_lat_lon(lat, lon, res_in_deg)
    nodeid = (xpix << 16) + ypix + 1
    return nodeid


def nodes_for_DTK(filename, nodes):
    with open(filename, "w") as f:
        json.dump(
            {"Nodes": [{"NodeID": n.id, "NodeAttributes": n.to_dict()} for n in nodes]},
            f,
            indent=4,
        )


def basicNode(lat: float = 0, lon: float = 0, pop: int = int(1e6), name: str = "node_name", forced_id: int = 1):
    return Node(lat, lon, pop, name=name, forced_id=forced_id)
