import arcpy
from arcpy import mp
import os

# out_folder = arcpy.GetParameterAsText(0)
out_folder = r"C:\ESRI_WORK_FOLDER\rtaa\layers"
# map_name = arcpy.GetParameterAsText(1)
map_name = "ViewerMap_01_18_17_D"
# source_gdb = arcpy.GetParameterAsText(2)
source_gdb = r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
# """For Testing"""
p = mp.ArcGISProject(r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\RTAA_publishing.aprx")
# p = mp.ArcGISProject('current')
p.save()
m = p.listMaps(map_name)[0]
flayers = [x for x in m.listLayers() if x.isFeatureLayer]
for lyr in flayers:
    layer_name = lyr.name.replace(" ", "_")
    old_info = lyr.connectionProperties
    new_dataset = lyr.name.replace("_", "")
    new_workspace_factory = "File Geodatabase"
    new_connection_info = {
        "database": source_gdb
    }
    new_info = {
        "dataset": new_dataset,
        "workspace_factory": new_workspace_factory,
        "connection_info": new_connection_info
    }
    lyr.updateConnectionProperties(old_info, new_info)
    i = 0
    for dirpath, dirs, files in os.walk(out_folder):
        for file in files:
            name = file.replace(".lyrx", "")
            if layer_name == name:
                save_path = os.path.join(dirpath, file)
                if not i:
                    os.remove(save_path)
                    # arcpy.SaveToLayerFile_management(l, save_path)
                    lyr.saveACopy(save_path)
                    arcpy.AddMessage("Saved layer {} to file".format(name))
                    i += 1
                    break
                else:
                    arcpy.AddWarning("Layer {} has already been saved, check for duplicate layers".format(name))
    if not i:
        arcpy.AddError(
            "Unable to save layer file {}.  It must exist in the folder to be overwritten".format(layer_name))