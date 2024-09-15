# Migration

This submodule provides scripts for creating (and reading) migration input files that are directly ingested by the DTK (EMOD) for determining how individuals migrate between nodes over time during a simulation. Going forward, all reading and writing of these migration control files should be done via this submodule.

It currently consists of a migration script for reading a DTK migration file (not writing yet). Sample usage:

  - ` import emod_api.migration.migration as mig`
  - ` MyMigrationFile = mig.MigrationFile(filename=filename)`
  - ` node_destination_rates = MyMigrationFile.rates()`

