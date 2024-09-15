# "The Gathering" - scripts imported from dtk-tools

## Available utilities

### migration/createmigrationheader.py

```bash
python -m emod_api.dtk_tools.migration.createmigrationheader <demographics.compiled.json>
```

Does not appear to be functional.

### serialization/dtkFileTests.py

```bash
python -m emod_api.dtk_tools.serialization.dtkFileTests
```

Unittests for dtkFileTools.

### serialization/dtkFileToolsToo.py

Old version of dtkFileTools/dtkFileUtility - should be deprecated.

### serialization/dtkFileUtility.py

```bash
python -m emod_api.dtk_tools.serialization.dtkFileUtility read emod_api\tests\data\serialization\version4.dtk
```

```bash
python -m emod_api.dtk_tools.serialization.dtkFileUtility write <output-file> <simulation-data.json> <node1-data.json> ... <nodeN-data.json>
```

### serialization/idtkFileTools.py

```bash
python -m emod_api.dtk_tools.serialization.idtkFileTools write --help
```

```bash
python -m emod_api.dtk_tools.serialization.idtkFileTools read --help
```

It looks like `idtkFileTools` is out of date (different schema for .dtk files).

### serialization/serialized_file_mc_to_sc.py

```bash
python -m emod_api.dtk_tools.serialization.serialized_file_mc_to_sc --help
```

Consolidates a set of serialized populations from a multi-core job to a single-core serialized population file. Hardcoded (1) for a 24-core job and (2) to default to time step 365 (can be changed from the command line).

### serialization/testTools.py

```bash
python -m emod_api.dtk_tools.serialization.testTools --help
```

(Re)creates one of more test files for the serialization tests. Depends on `test-data/baseline.dtk` to be present as the starting point.

### support/compiledemog.py

```bash
python -m emod_api.dtk_tools.support.compiledemog <path-to-demographics.json>
```

"Compiles" the normal JSON file by substituting two character keys for longer keys normally found in a demographics file. Writes the results to <path-to-demographics.compiled.json>.

### utilities/display_climate.py

```bash
python -m emod_api.dtk_tools.utilities.display_climate
```

Displays a year of air temperature and rainfall in the style of [weather-radials.com](http://www.weather-radials.com/). Weather files are currently hardcoded in the script. Needs modification to specify weather files on the command line.

### utilities/visualize_nodes.py

```bash
python -m emod_api.dtk_tools.utilities.visualize_nodes <path-to-demographics>
```

Displays plot of location of demographic nodes (try with Seattle demographics).

### utilities/visualize_routes.py

```bash
python -m emod_api.dtk_tools.utilities.visualize_routes <path-to-demographics> <path-to-migration.bin> <output-directory>
```

Writes migration_visualization.png to \<output-directory\> (try with Seattle demographics and local migration)

## Supporting code (no `main()`)

* climate/ClimateFileCreator.py
* demographics/DemographicsFile.py
* demographics/DemographicsGenerator.py
* demographics/DemographicsGeneratorConcern.py
* migration/LinkRatesModelGenerator.py
* migration/MigrationFile.py
* migration/MigrationGenerator.py
* migration/StaticLinkRatesModelGenerator.py
* reports/SpatialOutput.py
* serialization/dtkFileSupport.py
* serialization/dtkFileTools.py
* support/BaseInputFile.py
* support/demographics.py
* support/General.py
* support/Node.py
