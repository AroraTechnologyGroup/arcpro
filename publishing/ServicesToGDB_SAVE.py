import arcpy
from arcpy import mp
import os
import json
from arcpy import env

dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "services_dictionary.json")
if not os.path.exists(dict_path):
    arcpy.AddWarning("No service name dictionary exists to match service layers with their feature class parent.")
    raise Exception()

services = open(dict_path, 'r')
layer_mappings = json.loads(services.read())

out_folder = arcpy.GetParameterAsText(0)
# out_folder = r"D:\ArcPro\RTAA_Printing_Publishing\FeatureLayers"
map_name = arcpy.GetParameterAsText(1)
# map_name = "Viewer Map_2_26_B"
source_gdb = arcpy.GetParameterAsText(2)
# source_gdb = r"D:\EsriGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
# """For Testing"""
# p = mp.ArcGISProject(r"D:\ArcPro\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx")
p = mp.ArcGISProject('current')
p.save()
m = p.listMaps(map_name)[0]
flayers = [x for x in m.listLayers() if x.isFeatureLayer]
for lyr in flayers:
    layer_name = lyr.name.split("\\")[-1]
    layer_file_name = layer_name.replace(" ", "_")
    featureclass_name = layer_file_name.replace("_", "")
    try:
        old_info = lyr.connectionProperties
        i = 0
        new_dataset = []
        for x in layer_mappings:
            if x["FeatureClass"] == featureclass_name:
                new_dataset.append(featureclass_name)
                i += 1
                break
            elif layer_file_name in x["PublishedLayers"]:
                new_dataset.append(x["FeatureClass"])
                i += 1
                break

        if not i:
            # the feature class does not have multiple layer children, use standard feature class naming
            env.workspace = source_gdb
            datasets = arcpy.ListDatasets()
            for d in datasets:
                env.workspace = os.path.join(source_gdb, d)
                fclist = arcpy.ListFeatureClasses("*.{}".format(featureclass_name))
                arcpy.AddMessage("feature classes matching fcname {} = {}".format(featureclass_name, fclist))
                if len(fclist):
                    new_dataset.append(fclist[0])
                    i += 1
                    break
        if not i:
            arcpy.AddWarning("no feature class was found to be the parent of layer {}".format(old_info))
            raise Exception()

        new_workspace_factory = "File Geodatabase"
        new_connection_info = {
            "database": source_gdb
        }
        new_info = {
            "dataset": new_dataset[0],
            "workspace_factory": new_workspace_factory,
            "connection_info": new_connection_info
        }
        lyr.updateConnectionProperties(old_info, new_info)
        i = 0
        for dirpath, dirs, files in os.walk(out_folder):
            for file in files:
                name = file.replace(".lyrx", "")
                if layer_file_name == name:
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

    except Exception as e:
        arcpy.AddWarning("{}".format(e))
