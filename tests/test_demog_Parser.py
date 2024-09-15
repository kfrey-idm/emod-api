#!/usr/bin/env python
import unittest.mock
import io
import pandas as pd

import emod_api.demographics.DemographicsInputDataParsers as didp
from emod_api.demographics.Node import Node


class TestDemogParsers(unittest.TestCase):
    def setUp(self) -> None:
        print(f"\n{self._testMethodName} started...")

    # def test_help_function(self):
    #     import sys
    #     capturedOutput = io.StringIO()
    #     sys.stdout = capturedOutput
    #     help(didp)
    #     sys.stdout = sys.__stdout__
    #     self.assertIn('DESCRIPTION', capturedOutput.getvalue())
    #
    # @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    # def assert_help_stdout(self, n, expected_output, mock_stdout):
    #     help(n)
    #     self.assertIn(expected_output, mock_stdout.getvalue())
    #
    # def test_help_function(self):
    #     self.assert_help_stdout(didp, 'DESCRIPTION')

    def test_node_ID_from_lat_long(self):
        node_id = didp.node_ID_from_lat_long(lat=1000, long=1000, res=30 / 3600)
        node_id_2 = didp.node_ID_from_lat_long(lat=1000, long=1000, res=30 / 3600)
        self.assertEqual(node_id, node_id_2)

        node_id_3 = didp.node_ID_from_lat_long(lat=1000, long=1000, res=30 / 360)
        self.assertNotEqual(node_id, node_id_3)

        node_id_4 = didp.node_ID_from_lat_long(lat=999, long=1000, res=30 / 3600)
        self.assertNotEqual(node_id, node_id_4)

        node_id_5 = didp.node_ID_from_lat_long(lat=1000, long=1001, res=30 / 3600)
        self.assertNotEqual(node_id, node_id_5)

    def test_duplicate_nodeID_check(self):
        nodelist = []
        for item in [0, 0, 1, 2, 3, 5, 55, 55]:
            new_node = Node(item, item, 1234)
            nodelist.append(new_node)
        node_ids = pd.Series([n.id for n in nodelist])
        self.assertFalse(node_ids.is_unique)
        didp.duplicate_nodeID_check(nodelist)
        node_ids_2 = pd.Series([n.id for n in nodelist])
        self.assertTrue(node_ids_2.is_unique)


if __name__ == '__main__':
    unittest.main()
