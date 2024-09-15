# Demographics

This submodule provides scripts for creating what we have historically referred to as the demographis.json, an input file (or files) that are directly ingested by the DTK (EMOD) for determining how many nodes are in the model, and how many humans are in a given node, including vital dynamics like fertility and mortality.

We support the following capabilities:
- Read and parse various types of csv population data (into a list of Node objects).
    - fileformats are TBD but also pluggable in a sense that is to be clarified.
- User can set all the Default IndividualAttributes, including:
    - Birth rates
    - Death rates
    - Susceptibility
    - Initial Prevalence
    - Risk
    - User can set some presets for vital dynamics, accessing some built-in or provide their own.
- User can set all the Default NodeAttributes, including:
    - TBD
- User can set node-specific values for any of the above.
- User can set IndividualProperties.
    - User can set HINT matrices.
    - User can set Transition matrices.
- User can write out all this out to a DTK-compatible demographics.json file.
