# InsetCharts

This submodule provides scripts for interacting with what we have historically called the InsetChart.json output file produced by the DTK (EMOD). This file is sometimes called the Built-In or Default Report. It is a json formatted file that consists of channels of time-series data.

### Getting Started

```python
from emod_api.channelreports.channels import ChannelReport, Channel
```

### Tutorials

##### Loading an Existing Inset Chart File (or other channel report)

Pass a valid filename to ChannelReport, ```ChannelReport(filename)```, to create a ChannelReport object from an existing file.

### Sample Projects

### API Reference

<details><summary><b>ChannelReport</b></summary>

```ChannelReport(filename=None, **kwargs)``` Create a new ChannelReport from a file or, optionally, blank with the specified metadata.

```ChannelReport.dtk_version``` &#8594; DTK/EMOD version for this report

```ChannelReport.time_stamp``` &#8594; creation time stamp for this report

```ChannelReport.report_type``` &#8594; report type for this report (generally "InsetChart")

```ChannelReport.report_version``` &#8594; report version for this report

```ChannelReport.step_size``` &#8594; time delta for time steps in this report

```ChannelReport.start_time``` &#8594; initial time step for this report

```ChannelReport.num_time_steps``` &#8594; number of time steps (data values) per channel in this report

```ChannelReport.num_channels``` &#8594; number of channels in this report

```ChannelReport.channel_names``` &#8594; list of channel names/titles for this report

```ChannelReport.channels``` &#8594; dictionary of name/title:Channel for this report

```ChannelReport[channel_title]``` &#8594; Channel object from channels retrieved by name/title

```ChannelReport.as_dataframe()``` &#8594; pandas DataFrame with channel names/titles for column headers.  
**Note:** using this method requires pandas to be installed on the local machine. Otherwise, pandas is not a requirement.

```ChannelReport.write_file(filename, indent=0, separators=(',', ':'))``` Write this report, as JSON, to the specified file.
</details>

<details><summary><b>Channel</b></summary>

```Channel(title, units, data)``` Create a new inset chart Channel object with the given title, units (string), and data.

```Channel.title``` &#8594; string

```Channel.units``` &#8594; string

```Channel.data``` &#8594; time series data

```Channel[index]``` R/W access to channel time series data. Supports slices, e.g., `channel[31:59]`.

```Channel.as_dictionary()``` &#8594; dictionary representation of this Channel object. `{title:{'Units':units, 'Data':data}`
</details>

### Architecture Documentation

[reference](http://www.idmod.org/docs/general/software-report-inset-chart.html)

### Other

**Note**: requires pandas if using ```ChannelReport.as_dataframe()```

To test the submodule:  
```bash
python -m emod_api.tests.channel_reports
```

To run the example:
```bash
python -m emod_api.examples.insetchart
```