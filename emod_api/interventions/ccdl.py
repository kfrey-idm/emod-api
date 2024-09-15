"""
# Proto-schema

WHEN :: WHERE :: WHO :: WHAT

WHEN: <Start_Time>-<End_Time> OR <Start_Time>(x<Repetitions>/<Time_BetweenReps>)

WHERE: AllPlaces OR Node_List

WHO: <Coverage%>/<IP>/<Min_Age>/<Max_Age>/<Sex>

WHAT: <Triggers>-><Intervention_Name1(Payload)>+<Intervention_Name2(Payload)>+...

"""

# CCDL constants
main_sep = " :: "
multi_trigger_sep = "+"
multi_iv_sep = "+"
post_trigger_sep = "->"
post_delay_sep = "=>"
multi_signal_sep = "/"
WHEN_IDX = 0
WHERE_IDX = 1
WHO_IDX = 2
WHAT_IDX = 3
