from emod_api.demographics.Updateable import Updateable
from typing import List


class IndividualProperty(Updateable):
    def __init__(self,
                 initial_distribution: List[float] = None,
                 property=None,
                 values: List[float] = None,
                 transitions: List[float] = None,
                 transmission_matrix: List[float] = None
                 ):
        super().__init__()
        self.initial_distribution = initial_distribution
        self.property = property
        self.values = values
        self.transitions = transitions
        self.transmission_matrix = transmission_matrix

    def to_dict(self) -> dict:
        individual_property = self.parameter_dict

        if self.initial_distribution is not None:
            individual_property.update({"Initial_Distribution": self.initial_distribution})

        if self.property is not None:
            individual_property.update({"Property": self.property})

        if self.values is not None:
            if self.property == "Age_Bin":
                individual_property.update({"Age_Bin_Edges_In_Years": self.values})
            else:
                individual_property.update({"Values": self.values})

        if self.transitions is not None:
            individual_property.update({"Transitions": self.transitions})

        if self.transmission_matrix is not None:
            individual_property.update({"TransmissionMatrix": self.transmission_matrix})
        return individual_property


class IndividualProperties(Updateable):
    def __init__(self, individual_property: IndividualProperty = None):
        super().__init__()
        self.individual_properties = [individual_property] if individual_property else None

    def add(self, individual_property):
        if not self.individual_properties:
            self.individual_properties = []
        self.individual_properties.append(individual_property)

    def add_parameter(self, key, value):
        raise NotImplementedError("A parameter cannot be added to IndividualProperties.")

    def to_dict(self) -> dict:
        individual_properties = []
        for ip in self.individual_properties:
            individual_properties.append(ip.to_dict())
        return individual_properties

    def __getitem__(self, index: int):
        return self.individual_properties[index]

    def __len__(self):
        if not self.individual_properties:
            return 0
        return len(self.individual_properties)


class IndividualAttributes(Updateable):
    class SusceptibilityDistribution(Updateable):
        def __init__(self,
                     distribution_values: List[float] = None,
                     result_scale_factor=None,
                     result_values=None):
            super().__init__()
            self.distribution_values = distribution_values
            self.result_scale_factor = result_scale_factor
            self.result_values = result_values

        def to_dict(self) -> dict:
            susceptibility_distribution = self.parameter_dict

            if self.distribution_values is not None:
                susceptibility_distribution.update({"DistributionValues": self.distribution_values})

            if self.result_scale_factor is not None:
                susceptibility_distribution.update({"ResultScaleFactor": self.result_scale_factor})

            if self.result_values is not None:
                susceptibility_distribution.update({"ResultValues": self.result_values})

            return susceptibility_distribution

    class AgeDistribution(Updateable):
        def __init__(self,
                     distribution_values=None,
                     result_scale_factor=None,
                     result_values=None):
            super().__init__()
            self.distribution_values = distribution_values
            self.result_scale_factor = result_scale_factor
            self.result_values = result_values

        def to_dict(self) -> dict:
            age_distribution = {}

            if self.distribution_values is not None:
                age_distribution.update({"DistributionValues": self.distribution_values})

            if self.result_scale_factor is not None:
                age_distribution.update({"ResultScaleFactor": self.result_scale_factor})

            if self.result_values is not None:
                age_distribution.update({"ResultValues": self.result_values})

            return age_distribution

        def from_dict(self, age_distribution: dict):
            if age_distribution is not None:
                self.distribution_values = age_distribution.get("DistributionValues")
                self.result_scale_factor = age_distribution.get("ResultScaleFactor")
                self.result_values = age_distribution.get("ResultValues")
                self.num_dist_axes = age_distribution.get("NumDistributionAxes")
                self.results_units = age_distribution.get("ResultUnits")
            return self

    class FertilityDistribution(Updateable):
        def __init__(self,
                     axis_names: List[str] = None,
                     axis_scale_factors: List[float] = None,
                     axis_units=None,
                     num_distribution_axes=None,
                     num_population_axes=None,
                     num_population_groups=None,
                     population_groups=None,
                     result_scale_factor=None,
                     result_units=None,
                     result_values=None):
            super().__init__()
            self.axis_names = axis_names
            self.axis_scale_factors = axis_scale_factors
            self.axis_units = axis_units
            self.num_distribution_axes = num_distribution_axes
            self.num_population_axes = num_population_axes
            self.num_population_groups = num_population_groups
            self.population_groups = population_groups
            self.result_scale_factor = result_scale_factor
            self.result_units = result_units
            self.result_values = result_values

        def to_dict(self) -> dict:
            fertility_distribution = self.parameter_dict

            if self.axis_names is not None:
                fertility_distribution.update({"AxisNames": self.axis_names})

            if self.axis_scale_factors is not None:
                fertility_distribution.update({"AxisScaleFactors": self.axis_scale_factors})

            if self.axis_units is not None:
                fertility_distribution.update({"AxisUnits": self.axis_units})

            if self.num_distribution_axes is not None:
                fertility_distribution.update({"NumDistributionAxes": self.num_distribution_axes})

            if self.num_population_groups is not None:
                fertility_distribution.update({"NumPopulationGroups": self.num_population_groups})

            if self.population_groups is not None:
                fertility_distribution.update({"PopulationGroups": self.population_groups})

            if self.result_scale_factor is not None:
                fertility_distribution.update({"ResultScaleFactor": self.result_scale_factor})

            if self.result_units is not None:
                fertility_distribution.update({"ResultUnits": self.result_units})

            if self.result_values is not None:
                fertility_distribution.update({"ResultValues": self.result_values})

            return fertility_distribution

        def from_dict(self, fertility_distribution: dict):
            if fertility_distribution:
                self.axis_names = fertility_distribution.get("AxisNames")
                self.axis_scale_factors = fertility_distribution.get("AxisScaleFactors")
                self.axis_units = fertility_distribution.get("AxisUnits")
                self.num_distribution_axes = fertility_distribution.get("NumDistributionAxes")
                self.num_population_groups = fertility_distribution.get("NumPopulationGroups")
                self.population_groups = fertility_distribution.get("PopulationGroups")
                self.result_scale_factor = fertility_distribution.get("ResultScaleFactor")
                self.result_units = fertility_distribution.get("ResultUnits")
                self.result_values = fertility_distribution.get("ResultValues")
            return self

    class MortalityDistribution(Updateable):
        def __init__(self,
                     axis_names: List[str] = None,
                     axis_scale_factors: List[float] = None,
                     axis_units=None,
                     num_distribution_axes=None,
                     num_population_axes=None,
                     num_population_groups=None,
                     population_groups=None,
                     result_scale_factor=None,
                     result_units=None,
                     result_values=None):
            super().__init__()
            self.axis_names = axis_names
            self.axis_scale_factors = axis_scale_factors
            self.axis_units = axis_units
            self.num_distribution_axes = num_distribution_axes
            self.num_population_axes = num_population_axes
            self.num_population_groups = num_population_groups
            self.population_groups = population_groups
            self.result_scale_factor = result_scale_factor
            self.result_units = result_units
            self.result_values = result_values

        def to_dict(self) -> dict:
            mortality_distribution = self.parameter_dict

            if self.axis_names is not None:
                mortality_distribution.update({"AxisNames": self.axis_names})

            if self.axis_scale_factors is not None:
                mortality_distribution.update({"AxisScaleFactors": self.axis_scale_factors})

            if self.axis_units is not None:
                mortality_distribution.update({"AxisUnits": self.axis_units})

            if self.num_distribution_axes is not None:
                mortality_distribution.update({"NumDistributionAxes": self.num_distribution_axes})

            if self.num_population_groups is not None:
                mortality_distribution.update({"NumPopulationGroups": self.num_population_groups})

            if self.population_groups is not None:
                mortality_distribution.update({"PopulationGroups": self.population_groups})

            if self.result_scale_factor is not None:
                mortality_distribution.update({"ResultScaleFactor": self.result_scale_factor})

            if self.result_units is not None:
                mortality_distribution.update({"ResultUnits": self.result_units})

            if self.result_values is not None:
                mortality_distribution.update({"ResultValues": self.result_values})

            return mortality_distribution

        def from_dict(self, mortality_distribution: dict):
            if mortality_distribution is None:
                return None

            self.axis_names = mortality_distribution.get("AxisNames")
            self.axis_scale_factors = mortality_distribution.get("AxisScaleFactors")
            self.axis_units = mortality_distribution.get("AxisUnits")
            self.num_distribution_axes = mortality_distribution.get("NumDistributionAxes")
            self.num_population_groups = mortality_distribution.get("NumPopulationGroups")
            self.population_groups = mortality_distribution.get("PopulationGroups")
            self.result_scale_factor = mortality_distribution.get("ResultScaleFactor")
            self.result_units = mortality_distribution.get("ResultUnits")
            self.result_values = mortality_distribution.get("ResultValues")
            return self

    def __init__(self,
                 age_distribution_flag=None,
                 age_distribution1=None,
                 age_distribution2=None,
                 age_distribution=None,
                 prevalence_distribution_flag=None,
                 prevalence_distribution1=None,
                 prevalence_distribution2=None,
                 immunity_distribution_flag=None,
                 immunity_distribution1=None,
                 immunity_distribution2=None,
                 risk_distribution_flag=None,
                 risk_distribution1=None,
                 risk_distribution2=None,
                 migration_heterogeneity_distribution_flag=None,
                 migration_heterogeneity_distribution1=None,
                 migration_heterogeneity_distribution2=None,
                 fertility_distribution=None,
                 mortality_distribution=None,
                 mortality_distribution_male=None,
                 mortality_distribution_female=None,
                 susceptibility_distribution=None
                 ):
        super().__init__()
        self.age_distribution_flag = age_distribution_flag
        self.age_distribution1 = age_distribution1
        self.age_distribution2 = age_distribution2
        self.age_distribution = age_distribution
        self.prevalence_distribution_flag = prevalence_distribution_flag
        self.prevalence_distribution1 = prevalence_distribution1
        self.prevalence_distribution2 = prevalence_distribution2
        self.immunity_distribution_flag = immunity_distribution_flag
        self.immunity_distribution1 = immunity_distribution1
        self.immunity_distribution2 = immunity_distribution2
        self.risk_distribution_flag = risk_distribution_flag
        self.risk_distribution1 = risk_distribution1
        self.risk_distribution2 = risk_distribution2
        self.migration_heterogeneity_distribution_flag = migration_heterogeneity_distribution_flag
        self.migration_heterogeneity_distribution1 = migration_heterogeneity_distribution1
        self.migration_heterogeneity_distribution2 = migration_heterogeneity_distribution2
        self.fertility_distribution = fertility_distribution
        self.mortality_distribution = mortality_distribution
        self.mortality_distribution_male = mortality_distribution_male
        self.mortality_distribution_female = mortality_distribution_female
        self.susceptibility_distribution = susceptibility_distribution

    def to_dict(self) -> dict:
        individual_attributes = self.parameter_dict
        if self.age_distribution_flag is not None:
            individual_attributes_age_distribution = {
                "AgeDistributionFlag": self.age_distribution_flag,
                "AgeDistribution1": self.age_distribution1,
                "AgeDistribution2": self.age_distribution2
            }
            individual_attributes.update(individual_attributes_age_distribution)
        else:
            if self.age_distribution:
                individual_attributes_age_distribution = {
                    "AgeDistribution": self.age_distribution.to_dict()
                }
                individual_attributes.update(individual_attributes_age_distribution)

        if self.prevalence_distribution_flag is not None:
            prevalence_distribution = {
                "PrevalenceDistributionFlag": self.prevalence_distribution_flag,
                "PrevalenceDistribution1": self.prevalence_distribution1,
                "PrevalenceDistribution2": self.prevalence_distribution2
            }
            individual_attributes.update(prevalence_distribution)

        if self.immunity_distribution_flag is not None:
            immunity_distribution = {
                "ImmunityDistributionFlag": self.immunity_distribution_flag,
                "ImmunityDistribution1": self.immunity_distribution1,
                "ImmunityDistribution2": self.immunity_distribution2
            }
            individual_attributes.update(immunity_distribution)

        if self.migration_heterogeneity_distribution_flag is not None:
            migration_heterogeneity_distribution = {
                "MigrationHeterogeneityDistributionFlag": self.migration_heterogeneity_distribution_flag,
                "MigrationHeterogeneityDistribution1": self.migration_heterogeneity_distribution1,
                "MigrationHeterogeneityDistribution2": self.migration_heterogeneity_distribution2
            }
            individual_attributes.update(migration_heterogeneity_distribution)

        if self.risk_distribution_flag is not None:
            risk_distribution = {
                "RiskDistributionFlag": self.risk_distribution_flag,
                "RiskDistribution1": self.risk_distribution1,
                "RiskDistribution2": self.risk_distribution2
            }
            individual_attributes.update(risk_distribution)

        if self.susceptibility_distribution is not None:
            individual_attributes.update({"SusceptibilityDistribution": self.susceptibility_distribution.to_dict()})

        if self.fertility_distribution is not None:
            individual_attributes.update({"FertilityDistribution": self.fertility_distribution.to_dict()})

        if self.mortality_distribution is not None:
            individual_attributes.update({"MortalityDistribution": self.mortality_distribution.to_dict()})

        if self.mortality_distribution_male is not None:
            individual_attributes.update({"MortalityDistributionMale": self.mortality_distribution_male.to_dict()})

        if self.mortality_distribution_female is not None:
            individual_attributes.update({"MortalityDistributionFemale": self.mortality_distribution_female.to_dict()})
        return individual_attributes

    def from_dict(self, individual_attributes: dict):
        self.age_distribution_flag = individual_attributes.get("AgeDistributionFlag")
        self.age_distribution1 = individual_attributes.get("AgeDistribution1")
        self.age_distribution2 = individual_attributes.get("AgeDistribution2")
        self.age_distribution = IndividualAttributes.AgeDistribution().from_dict(
            individual_attributes.get("AgeDistribution"))  # DISTRIBUTION_COMPLEX
        self.prevalence_distribution_flag = individual_attributes.get("PrevalenceDistributionFlag")
        self.prevalence_distribution1 = individual_attributes.get("PrevalenceDistribution1")
        self.prevalence_distribution2 = individual_attributes.get("PrevalenceDistribution2")
        self.immunity_distribution_flag = individual_attributes.get("ImmunityDistributionFlag")
        self.immunity_distribution1 = individual_attributes.get("ImmunityDistribution1")
        self.immunity_distribution2 = individual_attributes.get("ImmunityDistribution2")
        self.risk_distribution_flag = individual_attributes.get("RiskDistributionFlag")
        self.risk_distribution1 = individual_attributes.get("RiskDistribution1")
        self.risk_distribution2 = individual_attributes.get("RiskDistribution2")
        self.migration_heterogeneity_distribution_flag = individual_attributes.get(
            "MigrationHeterogeneityDistributionFlag")
        self.migration_heterogeneity_distribution1 = individual_attributes.get("MigrationHeterogeneityDistribution1")
        self.migration_heterogeneity_distribution2 = individual_attributes.get("MigrationHeterogeneityDistribution2")
        self.fertility_distribution = IndividualAttributes.FertilityDistribution().from_dict(
            individual_attributes.get("FertilityDistribution"))
        self.mortality_distribution = IndividualAttributes.MortalityDistribution().from_dict(
            individual_attributes.get("MortalityDistribution"))
        self.mortality_distribution_male = IndividualAttributes.MortalityDistribution().from_dict(
            individual_attributes.get("MortalityDistributionMale"))
        self.mortality_distribution_female = IndividualAttributes.MortalityDistribution().from_dict(
            individual_attributes.get("MortalityDistributionFemale"))
        return self


class NodeAttributes(Updateable):
    def __init__(self,
                 airport: int = None,
                 altitude=None,
                 area: float = None,
                 birth_rate: float = None,
                 country=None,
                 growth_rate: float = None,
                 name: str = None,
                 latitude: float = None,
                 longitude: float = None,
                 metadata: dict = None,
                 initial_population: int = None,
                 region: int = None,
                 seaport: int = None,
                 larval_habitat_multiplier: List[float] = None,
                 initial_vectors_per_species=None,
                 infectivity_multiplier: float = None,
                 extra_attributes: dict = None
                 ):
        super().__init__()
        self.airport = airport
        self.altitude = altitude
        self.area = area
        self.birth_rate = birth_rate
        self.country = country
        self.growth_rate = growth_rate
        self.initial_population = initial_population
        self.initial_vectors_per_species = initial_vectors_per_species
        self.larval_habitat_multiplier = larval_habitat_multiplier
        self.latitude = latitude
        self.longitude = longitude
        self.metadata = metadata
        self.name = name
        self.region = region
        self.seaport = seaport
        self.infectivity_multiplier = infectivity_multiplier
        self.extra_attributes = extra_attributes

    def from_dict(self, node_attributes: dict):
        self.airport = node_attributes.get("Airport")
        self.altitude = node_attributes.get("Altitude")
        self.area = node_attributes.get("Area")
        self.country = node_attributes.get("country")
        self.growth_rate = node_attributes.get("GrowthRate")
        self.name = node_attributes.get("FacilityName")
        self.latitude = node_attributes.get("Latitude")
        self.longitude = node_attributes.get("Longitude")
        self.metadata = node_attributes.get("Metadata")
        self.initial_population = node_attributes.get("InitialPopulation")
        self.larval_habitat_multiplier = node_attributes.get("LarvalHabitatMultiplier")
        self.initial_vectors_per_species = node_attributes.get("InitialVectorsPerSpecies")
        self.birth_rate = node_attributes.get("BirthRate")
        self.seaport = node_attributes.get("Seaport")
        self.region = node_attributes.get("Region")
        self.infectivity_multiplier = node_attributes.get("InfectivityMultiplier")
        return self

    def to_dict(self) -> dict:
        node_attributes = self.parameter_dict
        if self.birth_rate is not None:
            node_attributes.update({"BirthRate": self.birth_rate})

        if self.area is not None:
            node_attributes.update({"Area": self.area})

        if self.latitude is not None:
            node_attributes.update({"Latitude": self.latitude})

        if self.longitude is not None:
            node_attributes.update({"Longitude": self.longitude})

        if self.initial_population is not None:
            node_attributes.update({"InitialPopulation": int(self.initial_population)})

        if self.name:
            node_attributes.update({"FacilityName": self.name})

        if self.larval_habitat_multiplier is not None:
            node_attributes.update({"LarvalHabitatMultiplier": self.larval_habitat_multiplier})

        if self.initial_vectors_per_species:
            node_attributes.update({"InitialVectorsPerSpecies": self.initial_vectors_per_species})

        if self.airport is not None:
            node_attributes.update({"Airport": self.airport})

        if self.altitude is not None:
            node_attributes.update({"Altitude": self.altitude})

        if self.seaport is not None:
            node_attributes.update({"Seaport": self.seaport})

        if self.region is not None:
            node_attributes.update({"Region": self.region})

        if self.country is not None:
            node_attributes.update({"country": self.country})

        if self.growth_rate is not None:
            node_attributes.update({"GrowthRate": self.growth_rate})

        if self.metadata is not None:
            node_attributes.update({"Metadata": self.metadata})

        if self.infectivity_multiplier is not None:
            node_attributes.update({"InfectivityMultiplier": self.infectivity_multiplier})

        if self.extra_attributes is not None:
            node_attributes.update(self.extra_attributes)

        return node_attributes
