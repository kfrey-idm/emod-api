import unittest
from emod_api.demographics.PropertiesAndAttributes import IndividualProperty


class IndividualPropertiesTest(unittest.TestCase):
    def test_default_parameters_to_dict(self):
        individual_property = IndividualProperty()
        self.assertDictEqual(individual_property.to_dict(), {})  # empty, no keys/values added


