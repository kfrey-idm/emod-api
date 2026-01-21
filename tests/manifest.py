import os

current_directory = os.path.dirname(os.path.realpath(__file__))

output_folder = os.path.join(current_directory, 'output')
if not os.path.isdir(output_folder):
    os.mkdir(output_folder)

config_folder = os.path.join(current_directory, 'data', 'config')
if not os.path.isdir(config_folder):
    os.mkdir(config_folder)

demo_folder = os.path.join(current_directory, 'data', 'demographics')
if not os.path.isdir(demo_folder):
    os.mkdir(demo_folder)

campaign_folder = os.path.join(current_directory, 'data', 'campaign')
if not os.path.isdir(campaign_folder):
    os.mkdir(campaign_folder)

migration_folder = os.path.join(current_directory, 'data', 'migration')
if not os.path.isdir(migration_folder):
    os.mkdir(migration_folder)

proprep_folder = os.path.join(current_directory, 'data', 'propertyreports')
if not os.path.isdir(proprep_folder):
    os.mkdir(proprep_folder)

spatrep_folder = os.path.join(current_directory, 'data', 'spatialreports')
if not os.path.isdir(spatrep_folder):
    os.mkdir(spatrep_folder)

reports_folder = os.path.join(current_directory, 'data', 'reports')
if not os.path.isdir(reports_folder):
    os.mkdir(reports_folder)

serialization_folder = os.path.join(current_directory, 'data', 'serialization')
if not os.path.isdir(serialization_folder):
    os.mkdir(serialization_folder)

weather_folder = os.path.join(current_directory, 'data', 'weatherfiles')
if not os.path.isdir(weather_folder):
    os.mkdir(weather_folder)


def delete_existing_file(file):
    if os.path.isfile(file):
        print(f'\tremove existing {file}.')
        os.remove(file)


def create_folder(folder_path):
    if folder_path:
        if not os.path.isdir(folder_path):
            print(f"\t{folder_path} doesn't exist, creating {folder_path}.")
            os.mkdir(folder_path)


mortality_data_age_year_csv = os.path.join(demo_folder, "India_mortality_1990_to_2017.csv")
mortality_reference_output = os.path.join(demo_folder, "india_mortality_reference_output.json")
fertility_reference_output = os.path.join(demo_folder, "fertility_reference_output.json")
ltm_csv_path = os.path.join(demo_folder, "ltm.csv")

package_folder = os.path.join(current_directory, 'package')
if not os.path.isdir(package_folder):
    os.mkdir(package_folder)

malaria_package_folder = os.path.join(package_folder, 'malaria')
malaria_eradication_path = os.path.join(malaria_package_folder, 'Eradication')
malaria_schema_path = os.path.join(malaria_package_folder, 'schema.json')
if not os.path.isfile(malaria_schema_path):
    print(f'Schema does not exist, writing it to {malaria_package_folder}.')
    import emod_malaria.bootstrap as dtk
    dtk.setup(malaria_package_folder)
