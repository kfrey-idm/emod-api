import emod_api.interventions.utils as utils
import unittest


import emod_api.schema_to_class as s2c



class UtilTest(unittest.TestCase):

    def setUp(self) -> None:
        print(f"\n{self._testMethodName} has started...")
    
    def tearDown(self) -> None:
        pass
    
    def test_do_nodes(self):
        # Case: node id list is full
        self.schema_path = "./data/config/input_generic_schema.json"

        node_ids = [1, 7, 9, 10]
        nodelist = utils.do_nodes(self.schema_path, node_ids)
        self.assertEqual(nodelist['class'], 'NodeSetNodeList')
        self.assertEqual(nodelist['Node_List'], node_ids)

        # Case: node id list is empty
        node_ids = []
        nodelist = utils.do_nodes(self.schema_path, node_ids)
        self.assertEqual(nodelist['class'], 'NodeSetAll')
        # checking that there is no node list
        nodelist.finalize()
        self.assertEqual(1, len(nodelist))

    def test_waning_from_params(self):
        self.schema_path = "./data/config/input_generic_schema.json"
        # test default 1 year full efficacy
        waning = utils.get_waning_from_params(self.schema_path)
        self.assertEqual(waning['Box_Duration'], 365)
        self.assertEqual(waning['Decay_Time_Constant'], 0)
        self.assertEqual(waning['Initial_Effect'], 1.0)
        self.assertEqual(waning['class'], 'WaningEffectBoxExponential')

        # test changing defaults
        waning = utils.get_waning_from_params(self.schema_path, initial=0.8, box_duration=300, decay_rate=0.1)
        self.assertEqual(waning['Box_Duration'], 300)
        self.assertEqual(waning['Decay_Time_Constant'], 10)
        self.assertEqual(waning['Initial_Effect'], 0.8)
        self.assertEqual(waning['class'], 'WaningEffectBoxExponential')

        # test waning effect constant
        waning = utils.get_waning_from_params(self.schema_path, initial=0.8, box_duration=-1, decay_rate=0.1)   
        self.assertEqual(waning['class'], 'WaningEffectConstant')
        self.assertEqual(waning['Initial_Effect'], 0.8)





