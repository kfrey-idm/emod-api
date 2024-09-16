import unittest
from emod_api.demographics.PropertiesAndAttributes import IndividualProperty


class IndividualPropertiesTest(unittest.TestCase):
    def test_default_parameters_to_dict(self):
        individual_property = IndividualProperty(property='blah')
        self.assertDictEqual(individual_property.to_dict(), {'Property': 'blah'})  # empty, no keys/values added


