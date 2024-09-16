import sys
import emod_api.demographics.Demographics as Dem
import os
import unittest
import pandas as pd
import json
from emod_api.demographics.service import grid_construction as grid
import numpy as np
from datetime import date
import getpass

class DemogFromPop(unittest.TestCase):
    def setUp(self):
        if os.path.exists("burkina_demog.json"):
           os.remove("burkina_demog.json") 
        super().setUp()
        pass

    def tearDown(self):
        if os.path.exists("spatial_gridded_pop_dir/No_Site_grid.csv"):
            os.remove("spatial_gridded_pop_dir/No_Site_grid.csv")
        if os.path.exists("spatial_gridded_pop_dir/No_Site_grid_id_2_cell_id.json"):
            os.remove("spatial_gridded_pop_dir/No_Site_grid_id_2_cell_id.json")      
        super().tearDown()
        pass


    # Basic consistency test for demographic creation 
    # Checks creation of demographics object from
    def test_demo_from_pop_basic(self):
        if os.path.exists("burkina_demog.json"):
            os.remove("burkina_demog.json")
        input_path = "data/tiny_facebook_pop_clipped.csv"
        point_records = pd.read_csv(input_path, encoding="iso-8859-1")
        point_records.rename(columns={'longitude': 'lon', 'latitude': 'lat'}, inplace=True)

        # Checking that the populations are comparable
        inputdata = pd.read_csv(input_path)

        #Aggregating grid squares to check grid against population
        #Can find a way to make this more efficient later (only parse the pop column)
        x_min, y_min, x_max, y_max = grid.get_bbox(point_records)
        point_records = point_records[
            (point_records.lon >= x_min) & (point_records.lon <= x_max) & (point_records.lat >= y_min) & (
                    point_records.lat <= y_max)]
        gridd, grid_id_2_cell_id, origin, final = grid.construct(x_min, y_min, x_max, y_max)


        point_records[['gcid', 'gidx', 'gidy']] = point_records.apply(
                grid.point_2_grid_cell_id_lookup,
                args=(grid_id_2_cell_id, origin,), axis=1).apply(pd.Series)

        grid_pop = point_records.groupby(['gcid', 'gidx', 'gidy'])['pop'].apply(np.sum).reset_index()

        # Leaving a berth of 10 for rounding, may need to check later
        self.assertTrue(abs(grid_pop['pop'].sum() - inputdata['pop'].sum()) < 10)

        demog = Dem.from_pop_raster_csv(input_path)
        self.assertTrue(os.path.isfile("spatial_gridded_pop_dir/No_Site_grid.csv"), msg=f"No_Site_grid.csv is not generated.")


        gridfile = pd.read_csv("spatial_gridded_pop_dir/No_Site_grid.csv")

        demog.SetDefaultProperties()

        demog.generate_file("burkina_demog.json")
        self.assertTrue(os.path.isfile("burkina_demog.json"), msg=f"burkina_demog.json is not generated.")

        # Checking consistency between burkina and grid files

        with open("burkina_demog.json") as json_file: 
            burkina = json.load(json_file) 
        burkina_nodes = burkina['Nodes']

        for index, node in enumerate(burkina_nodes):
            features = node['NodeAttributes']
            self.assertEqual(features['Longitude'], gridfile['lon'][index])
            self.assertEqual(features['Latitude'], gridfile['lat'][index])
            self.assertEqual(features['InitialPopulation'], gridfile['pop'][index])

        # Checking metadata
        metadata = burkina['Metadata']
        today = date.today()
        self.assertEqual(metadata['DateCreated'], today.strftime("%m/%d/%Y"))
        self.assertEqual(metadata['Tool'], "emod-api")
        self.assertEqual(metadata['NodeCount'], len(burkina_nodes))
        self.assertEqual(metadata['Author'], getpass.getuser())

