def set( config ):
    config.parameters.Enable_Default_Reporting = 1
    config.parameters.This_Param_Does_Not_Exist = "gotcha"
    return config
