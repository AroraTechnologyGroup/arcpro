import os
import arcpy
from arcpy import env

"""
Use this tool to build the layer files storage directories

This Tool loops through the datasets in the input geodatabase, if the name of the dataset does not exist
as a folder in the output directory, a new folder is created.
"""

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
