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
        self.schema_path = "./data/config/input_generic_schema_waning.json"

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
        self.schema_path = "./data/config/input_generic_schema_waning.json"
        # test default 1 year full efficacy
        # box_duration > 0 + decay_time_constant = 0 => WaningEffectBox
        waning = utils.get_waning_from_params(self.schema_path)
        self.assertEqual(waning['Box_Duration'], 365)
        self.assertEqual(waning['Initial_Effect'], 1.0)
        self.assertEqual(waning['class'], 'WaningEffect')

        # test changing defaults
        #  box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential  ; decay_time_constant 1/decay_rate
        waning = utils.get_waning_from_params(self.schema_path, initial=0.8, box_duration=300, decay_rate=0.1)
        self.assertEqual(waning['Box_Duration'], 300)
        self.assertEqual(waning['Decay_Time_Constant'], 10)
        self.assertEqual(waning['Initial_Effect'], 0.8)
        self.assertEqual(waning['class'], 'WaningEffect')

        # test waning effect constant
        # box_duration > 0 + decay_time_constant = 0 => WaningEffectBox/Constant (depending on duration)
        waning = utils.get_waning_from_params(self.schema_path, initial=0.8, box_duration=-1, decay_rate=0.1)   
        self.assertEqual(waning['class'], 'WaningEffect')
        self.assertEqual(waning['Initial_Effect'], 0.8)

    def test_get_waning_from_points(self):
        schema_path = "./data/config/input_generic_schema_waning.json"
        linear_expire_at_end = 1
        points = [(1, 2), (3, 4), (5, 6)]
        waning = utils.get_waning_from_points(schema_path, times_values=points, expire_at_end=linear_expire_at_end)
        self.assertEqual(waning['Durability_Map']['Times'], [1, 3, 5])
        self.assertEqual(waning['Durability_Map']['Values'], [2, 4, 6])
        self.assertEqual(waning['class'], 'WaningEffect')

    def test_get_exponential_waning_from_parameters_1(self):
        #  box_duration = 0 + decay_time_constant > 0 = > WaningEffectExponential
        schema_path = "./data/config/input_generic_schema_waning.json"
        initial = 0.75
        box_duration = 0  # constant
        decay_time_constant = 0.5
        waning = utils.get_waning_from_parameters(schema_path, initial=initial, box_duration=box_duration,
                                                  decay_time_constant=decay_time_constant)
        self.assertEqual(waning['class'], 'WaningEffect')
        self.assertEqual(waning['Initial_Effect'], initial)
        self.assertEqual(waning['Decay_Time_Constant'], decay_time_constant)

    def test_get_exponential_waning_from_parameters_2(self):
        #  box_duration > 0 + decay_time_constant = 0 = > WaningEffectBox / Constant(depending on duration)
        schema_path = "./data/config/input_generic_schema_waning.json"
        initial = 0.75
        box_duration = 1
        decay_time_constant = 0
        waning = utils.get_waning_from_parameters(schema_path, initial=initial, box_duration=box_duration,
                                                  decay_time_constant=decay_time_constant)
        self.assertEqual(waning['class'], 'WaningEffect')
        self.assertEqual(waning['Box_Duration'], box_duration)
        self.assertEqual(waning['Initial_Effect'], initial)

    def test_get_exponential_waning_from_parameters_3(self):
        #  box_duration > 0 + decay_time_constant = 0 = > WaningEffectBox / Constant(depending on duration)
        schema_path = "./data/config/input_generic_schema_waning.json"
        initial = 0.75
        box_duration = -1
        decay_time_constant = 0
        waning = utils.get_waning_from_parameters(schema_path, initial=initial, box_duration=box_duration,
                                                  decay_time_constant=decay_time_constant)
        self.assertEqual(waning['class'], 'WaningEffect')
        self.assertEqual(waning['Initial_Effect'], initial)

    def test_get_exponential_waning_from_parameters_3(self):
        #  box_duration > 0 + decay_time_constant > 0 = > WaningEffectBoxExponential
        schema_path = "./data/config/input_generic_schema_waning.json"
        initial = 0.75
        box_duration = 1
        decay_time_constant = 0.5
        waning = utils.get_waning_from_parameters(schema_path, initial=initial, box_duration=box_duration,
                                                  decay_time_constant=decay_time_constant)
        self.assertEqual(waning['class'], 'WaningEffect')
        self.assertEqual(waning['Initial_Effect'], initial)
        self.assertEqual(waning['Decay_Time_Constant'], decay_time_constant)


    def test_get_exponential_waning_from_parameters_decay(self):
        # box_duration > 0 + decay_time_constant > 0 => WaningEffectBoxExponential
        schema_path = "./data/config/input_generic_schema_waning.json"
        box_duration = 1
        initial = 0.75
        decay_rate = 2
        waning = utils.get_waning_from_parameters(schema_path, initial=initial, box_duration=box_duration, decay_rate=decay_rate)
        self.assertEqual(waning['class'], 'WaningEffect')
        self.assertEqual(waning['Box_Duration'], box_duration)
        self.assertEqual(waning['Initial_Effect'], initial)
        self.assertEqual(waning['Decay_Time_Constant'], 1/decay_rate)

    def test_get_exponential_waning_from_parameters_raise(self):
        schema_path = "./data/config/input_generic_schema_waning.json"
        box_duration = 2
        initial = 0.75
        decay_time_constant = -0.5

        with self.assertRaises(ValueError) as err:
            utils.get_waning_from_parameters(schema_path, initial=initial, box_duration=box_duration,
                                             decay_time_constant=decay_time_constant)
        #print(err.exception)

