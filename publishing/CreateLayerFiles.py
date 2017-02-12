import os
import arcpy
from arcpy import env

masterGDB = arcpy.GetParameterAsText(0)
outfolder = arcpy.GetParameterAsText(1)

env.workspace = masterGDB
datasets = arcpy.ListDatasets()
for d in datasets:
    env.workspace = os.path.join(masterGDB, d)
    fclist = arcpy.ListFeatureClasses()
    dfolder = os.path.join(outfolder, d)
    for fc in fclist:
        i = 0
        with arcpy.da.SearchCursor(fc, "*") as cursor:
            for row in cursor:
                i += 1
        if i:
            outlayer = arcpy.MakeFeatureLayer_management(fc, "{}".format(fc))
            outpath = os.path.join(dfolder, "{}.lyrx".format(fc))
            if not os.path.exists(outpath):
                arcpy.SaveToLayerFile_management(outlayer, outpath)
                if arcpy.Exists(outpath):
                    arcpy.AddMessage("Layer {}.lyrx was created".format(fc))
                else:
                    arcpy.AddError("Layer {}.lyrx failed to be created".format(fc))
            else:
                arcpy.AddWarning("Layer {}.lyrx already exists".format(fc))

            arcpy.Delete_management("outlayer")
        else:
            arcpy.AddMessage("Feature Class {} is empty.  No layer created".format(fc))
