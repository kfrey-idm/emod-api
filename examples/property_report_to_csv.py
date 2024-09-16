#! /usr/bin/env python3

"""Examples for `property_report_to_csv()`."""

from pathlib import Path
from tempfile import mkdtemp

from emod_api.channelreports.utils import property_report_to_csv
# from emod_api.channelreports.channels import ChannelReport

report_file = (Path(__file__).parent.parent / "tests" / "data" / "propertyreports" / "propertyReport.json").absolute()
if report_file.exists():
    print(f"Using '{report_file.absolute()}' as example property report.")
else:
    print(f"Default property report, '{report_file.absolue()}' not found. Exiting.")
    exit(1)

temp_dir = Path(mkdtemp())
print(f"Example results going into '{temp_dir}'")

# "default" usage - all channels, no groupby, do not transpose
# channels and groupby default to None, and transpose defaults to False
csv_file = temp_dir / "01-defaults.csv"
print(f"Writing all channels disaggregated to {csv_file}...")
property_report_to_csv(report_file, csv_file)

# Note - it is a little more efficient to call the following if using all the defaults:
# report = ChannelReport(str(source_file))
# report.to_csv(csv_file, channels=None, transpose=transpose)

# include a subset of available channels
# groupby defaults to None, and transpose defaults to False
csv_file = temp_dir / "02-selected-channels.csv"
print(f"Writing 'Infected' and 'New Infections' channels disaggregated to {csv_file}...")
property_report_to_csv(report_file, csv_file, channels=["Infected", "New Infections"])

# for one channel, use groupby to aggregate results
# transpose defaults to False
csv_file = temp_dir / "03-group-by-age.csv"
print(f"Writing 'Infected' channel (and 'Statistical Population' for normalization) grouped by 'Age_Bin' IPs to {csv_file}...")
property_report_to_csv(report_file, csv_file, channels=["Infected", "Statistical Population"], groupby=["Age_Bin"])

# for one channel, use groupby to aggregate results
# transpose defaults to False
csv_file = temp_dir / "04-no-stat-pop.csv"
print(f"Writing 'Infected' channel grouped by 'Age_Bin' IPs to {csv_file}...")
property_report_to_csv(report_file, csv_file, channels=["Infected"], groupby=["Age_Bin"])

# for one channel, use groupby to aggregate results, and transpose results - timesteps in rows
csv_file = temp_dir / "05-transpose.csv"
print(f"Writing 'Infected' channel grouped by 'Age_Bin' IPs transposed to timesteps in rows to {csv_file}...")
property_report_to_csv(report_file, csv_file, channels=["Infected"], groupby=["Age_Bin"], transpose=True)

# include "Statistical Population" for normalization purposes, use groupby to aggregate results, and transpose results - timesteps in rows
csv_file = temp_dir / "05-transpose.csv"
print(f"Writing 'Infected' channel (and 'Statistical Population') grouped by 'Age_Bin' IPs transposed to timesteps in rows to {csv_file}...")
property_report_to_csv(report_file, csv_file, channels=["Infected", "Statistical Population"], groupby=["Age_Bin"], transpose=True)
