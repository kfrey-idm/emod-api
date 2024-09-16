import unittest
import sys
from pathlib import Path

from emod_api.demographics.PropertiesAndAttributes import IndividualProperties, IndividualProperty

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))


class IndividualPropertiesTest(unittest.TestCase):

    def setUp(self):
        self.ip = IndividualProperty(property='in Arizona', values=['Yes', 'No'], initial_distribution=[0.01, 0.99])
        self.ips = IndividualProperties()
        self.ips.individual_properties = [self.ip]

        self.new_ip = IndividualProperty(property='in Florida', values=['Yes', 'No'],
                                         initial_distribution=[0.02, 0.98])
        self.new_ip_v2 = IndividualProperty(property='in Florida', values=['Yes', 'No'],
                                            initial_distribution=[0.03, 0.97])

    def tearDown(self):
        pass

    def test_has_individual_property_works(self):
        self.assertEqual(len(self.ips), 1)
        # non-existent ip
        self.assertFalse(self.ips.has_individual_property(property_key=self.new_ip.property))
        # existing ip
        self.assertTrue(self.ips.has_individual_property(property_key=self.ip.property))

    def test_remove_individual_property_works(self):
        self.assertEqual(len(self.ips), 1)
        # test removing non-existent ip
        self.ips.remove_individual_property(property_key=self.new_ip.property)
        self.assertEqual(len(self.ips), 1)
        # test removing existing ip
        self.ips.remove_individual_property(property_key=self.ip.property)
        self.assertEqual(len(self.ips), 0)

    def test_add_with_overwrite_works(self):
        self.assertEqual(len(self.ips), 1)

        # test adding truly new ip
        self.ips.add(individual_property=self.new_ip, overwrite=True)
        self.assertEqual(len(self.ips), 2)
        ip = self.ips.get_individual_property(property_key=self.new_ip.property)
        self.assertEqual(ip, self.new_ip)
        self.assertNotEqual(ip, self.new_ip_v2)

        # test adding a modified version of new ip, overwriting the previous version
        self.ips.add(individual_property=self.new_ip_v2, overwrite=True)
        self.assertEqual(len(self.ips), 2)
        ip = self.ips.get_individual_property(property_key=self.new_ip_v2.property)
        self.assertEqual(ip, self.new_ip_v2)
        self.assertNotEqual(ip, self.new_ip)

    def test_add_without_overwrite_works(self):
        self.assertEqual(len(self.ips), 1)

        # test adding truly new ip
        self.ips.add(individual_property=self.new_ip, overwrite=False)
        self.assertEqual(len(self.ips), 2)
        ip = self.ips.get_individual_property(property_key=self.new_ip.property)
        self.assertEqual(ip, self.new_ip)
        self.assertNotEqual(ip, self.new_ip_v2)

        # test adding a modified version of new ip; should throw an exception this time since not overwriting
        self.assertRaises(IndividualProperties.DuplicateIndividualPropertyException,
                          self.ips.add, individual_property=self.new_ip_v2, overwrite=False)

    def test_get_individual_property_works(self):
        # get a property we know exists
        ip = self.ips.get_individual_property(property_key=self.ip.property)
        self.assertEqual(ip, self.ip)

        # get a property we know does not exist
        self.assertRaises(IndividualProperties.NoSuchIndividualPropertyException,
                          self.ips.get_individual_property, property_key=self.new_ip.property)

