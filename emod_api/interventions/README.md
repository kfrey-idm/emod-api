# Campaign

This submodule provides scripts for creating what we have historically referred to as the campaign.json, an input file (or files) that are directly ingested by the DTK (EMOD) for distributing interventions to individuals (or nodes) at certain times during the simulation.


# Concise Campaign Definition Language (CCDL)

CCDL is a novel and experimental alternative way to represent campaigns. An existing campaign.json can be converted into CCDL for potentially easier human readability, and it is increasingly possible to create a campaign entirely in CCDL.

## Usage

The instructions below are linux-specific. If you remove the '3' suffix from pip3 and python3 they should work on Windows.

Install:
```
pip3 install emod-api --upgrade
```

Decode:
```
python3 -m emod_api.peek_camp -c <path/to/campaign.json>
```

Should give you something along the lines of:

```
5
365 :: AllPlaces :: 7.5% :: OutbreakIndividual
1 :: AllPlaces :: 100.0% :: HIVSymptomatic->HIVRandomChoice({'GetTested': 0.5, 'Ignore': 0.5})
1 :: AllPlaces :: 100.0% :: GetTested->DelayedIntervention(FIXED/30)=>HIVRapidHIVDiagnostic(HIVPositiveTest/HIVNegativeTest)
1 :: AllPlaces :: 100.0% :: HIVPositiveTest->DelayedIntervention(FIXED/30)=>BroadcastEvent(StartTreatment)
1 :: AllPlaces :: 100.0% :: StartTreatment->AntiretroviralTherapy
```
# Brief overview of CCDL Format/Schema
- The first number is just the total number of campaign events.
- Each campaign event is represented in a single line.
- The format is basically: When? :: Where? :: Who? :: What?
- If the What? section starts with "Something->", the Something is the trigger (or signal) that is being listened for. These are Triggered Events instead of Scheduled Events.
- This format is not intentioned to capture every detail in a campaign event.
- If the When? section has a (x10/_365), that means the Scheduled Event repeats 10 times every year.
- If the When? section has a -1234 component, that represents the limited duration.
- AllPlaces means AllNodes. 
- Each intervention has the most important attribute in parentheses. The meaning of these varies by intervention. Documentation of these is TBD.
- The Who? section is Coverage%/Sex/>Min_Age/<Max_Age/IP_Key=IP_Value. The parser is very dependent on the "shift-key symbols".
- Include multiple triggers or interventions by + -ing them together.
- DelayedIntervention is the only intervention that is followed by a => symbol.

For a slightly more ambitious example, use the rakai example campaign.json as input to produce:
```
19

# CSW
1 :: AllPlaces :: 3.0%/Female :: STIDebut->DelayedIntervention(FIXED/300)=>BroadcastEvent(CSW_Uptake)
1 :: AllPlaces :: 3.0%/Female :: CSW_Uptake->DelayedIntervention(FIXED/30)=>BroadcastEvent(CSW_Dropout)
1 :: AllPlaces :: 3.0%/Male :: STIDebut->DelayedIntervention(GAUSSIAN)=>BroadcastEvent(CSW_Uptake)
1 :: AllPlaces :: 3.0%/Male :: CSW_Uptake->DelayedIntervention(FIXED/300)=>BroadcastEvent(CSW_Dropout)
1 :: AllPlaces :: 100.0% :: CSW_Dropout->PropertyValueChanger(Risk:HIGH)
1 :: AllPlaces :: 100.0% :: CSW_Uptake->PropertyValueChanger(Risk:HIGH)

# STI Co-Inf
1 :: AllPlaces :: 10.0%/Risk=LOW :: ModifyStiCoInfectionStatus+BroadcastEvent(CaughtNonHIVSTI)
1 :: AllPlaces :: 10.0%/Risk=LOW :: STIDebut->ModifyStiCoInfectionStatus+BroadcastEvent(CaughtNonHIVSTI)
1 :: AllPlaces :: 30.0%/Risk=HIGH :: ModifyStiCoInfectionStatus+BroadcastEvent(CaughtNonHIVSTI)
1 :: AllPlaces :: 30.0%/Risk=HIGH :: STIDebut->ModifyStiCoInfectionStatus+BroadcastEvent(CaughtNonHIVSTI)
1 :: AllPlaces :: 30.0%/Risk=MEDIUM :: ModifyStiCoInfectionStatus+BroadcastEvent(CaughtNonHIVSTI)
1 :: AllPlaces :: 30.0%/Risk=MEDIUM :: STIDebut->ModifyStiCoInfectionStatus+BroadcastEvent(CaughtNonHIVSTI)

# Test & Treat
1 :: AllPlaces :: STEERED/Female/>15/<50/Accessibility=Easy :: AntiretroviralTherapy+DelayedIntervention(FIXED/36500)=>BroadcastEvent(ARTDropout)
1 :: AllPlaces :: STEERED/Male/>15/<50/Accessibility=Easy :: AntiretroviralTherapy+DelayedIntervention(FIXED/36500)=>BroadcastEvent(ARTDropout)
1 :: AllPlaces :: 100.0% :: HIVInfectionStageEnteredLatent->PropertyValueChanger(TestingStatus:ELIGIBLE)
1 :: AllPlaces :: 100.0% :: HIVInfectionStageEnteredLatent->PropertyValueChanger(TestingStatus:ELIGIBLE)
1 :: AllPlaces :: STEERED/Female/>15/<50/TestingStatus=ELIGIBLE :: PositiveStatusKnown(Accessibility:Easy)
1 :: AllPlaces :: STEERED/Male/>15/<50/TestingStatus=ELIGIBLE :: PositiveStatusKnown(Accessibility:Easy)

# Seed
365 :: AllPlaces :: 7.5% :: OutbreakIndividual
```
Now to be fair, we've done a bit of manual sorting and added some comments and spaces. But the original 47k, 1000-line campaign.json starts to tell us its story in a much more concise manner.

For campaign creation from CCDL, you'll want to use the pre-release of emodpy-hiv.

```
python3 -m pip install emodpy-hiv --upgrade --pre
```

To encode, aka create a campaign.json from a concise campaign definition file:
```
python3 -m emodpy_hiv.camp_creator <path/to/concise/campaign> <path/to/schema.json>
```

### TODO:
- Support time-value-maps as (separate labelled LUT items). This is in progress.

### FAQ
**Q.** Does this conversion work in both directions?

**A.** Yes. The 'peek_campaign' utility should be able to "decode" or "compress" a campaign.json file into a CCDL approximation (on the console). And the 'camp_creator' utility should be able to turn a .ccdl file into a campaign.json.

**Q.** How would this work with emodpy code?

**A.** Right now there are just utilities that go back-and-forth between campaign.json and CCDL formats. But the expectation is that the code in the utility will be brought into emod-api and emodpy* modules such that your "build_campaign" function just passes the path to a .ccdl file and emodpy will say 'oh, I have a function for converting that to a campaign.json'.

**Q.** Is this a code generation tool?

**A.** No, but that is an interesting idea. The code that creates campaigns from a CCDL file mostly uses the ScheduledCampaignEvent and TriggeredCampaignEvent functions in emod-api.interventions.common. It also uses some somewhat inelegant but parsimonious code to create interventions by name.

**Q.** How complex a campaign file can this format handle?

**A.** See the [eSwatini](eswatini.brief) example for the most complex we have handled to date.

**Q.** Is CCDL intended to support all the capabilities of legacy campaign building?

**A.** No. If you expect to be setting most or all of the parameters in an intervention or event coordinator, you'll want to learn to use the full Python API. CCDL is intended to make the 90% simple use case easier.

**Q.** How does this work with calibration?

**A.** That's an open question, but since each campaign event is a single line, it's pretty easy to imagine targeting a specific event by line id, and since each line is well-formed, it's pretty easy to imagine being able to target a particular element of a line for override.

**Q.** How hard would it be to make a GUI that let  you drag-and-drop campign events and visualize the relationship between "signals and slots" (published and subscribed signals or triggers)?

**A.** There are no such plans right now but it's pretty easy to imagine how this file format might facilitate that.
