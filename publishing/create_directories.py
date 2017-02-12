import os
import arcpy
from arcpy import env

masterGDB = arcpy.GetParameterAsText(0)
outfolder = arcpy.GetParameterAsText(1)

env.workspace = masterGDB
datasets = arcpy.ListDatasets()

for d in datasets:
    p = os.path.join(outfolder, d)
    if not os.path.exists(p):
        os.mkdir(p)
        if os.path.exists(p):
            arcpy.AddMessage("Folder {} was created".format(d))
        else:
            arcpy.AddError("Folder {} failed to be created".format(d))
    else:
        arcpy.AddWarning("Folder {} already exists".format(d))
