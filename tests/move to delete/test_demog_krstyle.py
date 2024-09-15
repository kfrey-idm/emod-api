import emod_api.demographics.Demographics as Demographics
import emod_api.demographics.DemographicsTemplates as DT


demog = Demographics.fromBasicNode( lat=0, lon=0, pop=1000, name=1, forced_id=1 )
demog.SetDefaultProperties()
DT.SimpleSusceptibilityDistribution(demog, meanAgeAtInfection=2.5 )
demog.AddAgeDependentTransmission( Age_Bin_Edges_In_Years=[0, 1, 2, -1], TransmissionMatrix=[[0.2, 0.4, 1.0], [0.2, 0.4, 1.0], [0.2, 0.4, 1.0]] )
demog.generate_file()

"""
Remaining capability to support:
    hint_bin = np.int(param.split('_')[-1])
    for demo_name, demo_content in CB.demog_overlays.items():
        matrix = np.array(demo_content['Defaults']['IndividualProperties'][0]['TransmissionMatrix']['Matrix'])
        matrix[:, hint_bin] = value
        demo_content['Defaults']['IndividualProperties'][0]['TransmissionMatrix']['Matrix'] = matrix.tolist()
"""
