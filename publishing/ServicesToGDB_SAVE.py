import arcpy
from arcpy import mp
import os
import json
from arcpy import env
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GDB_Utility import GDBReferenceObject

"""
Use this tool to pull down feature layer symbology from AGOL

1. The web map must be added to the project
2. Run this tool inside the Pro Project
"""
dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "services_dictionary.json")
if not os.path.exists(dict_path):
    arcpy.AddWarning("No service name dictionary exists to match service layers with their feature class parent.")
    raise Exception()

services = open(dict_path, 'r')
layer_mappings = json.loads(services.read())

# out_folder = arcpy.GetParameterAsText(0)
out_folder = r"D:\ArcPro\RTAA_Publishing\FeatureLayers"
# map_name = arcpy.GetParameterAsText(1)
map_name = "Viewer Map_2_26_B"
# source_gdb = arcpy.GetParameterAsText(2)
source_gdb = r"D:\EsriGDB\ConnectionFiles\Sub-Default_MasterGDB.sde"
gdb_dict = GDBReferenceObject(source_gdb)
gdb_obj = gdb_dict.build_dict()
# """For Testing"""
p = mp.ArcGISProject(r"D:\ArcPro\RTAA_Publishing\RTAA_Publishing.aprx")
# p = mp.ArcGISProject('current')
p.save()
m = p.listMaps(map_name)[0]
flayers = [x for x in m.listLayers() if x.isFeatureLayer]
for lyr in flayers:
    layer_name = lyr.name.split("\\")[-1]
    layer_file_name = layer_name.replace(" ", "_")
    # look up the feature class name from the services_dictionary using the layer_name
    featureclass_name = []
    for rec in layer_mappings:
        if layer_name in rec["PublishedLayers"]:
            featureclass_name.append(rec["FeatureClass"])
    if featureclass_name:
        featureclass_name = featureclass_name[0]
    else:
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
            # the feature class does not have multiple layer children so the services
            # dictionary is not needed, use standard feature class naming
            env.workspace = source_gdb

            for k, v in gdb_obj.items():
                base_names = [x.split(".")[-1] for x in v]
                if featureclass_name in base_names:
                    fcname = v[base_names.index(featureclass_name)]
                    new_dataset.append(fcname)
                    i += 1
                    break

        if not i:
            raise Exception("no feature class was found to be the parent of layer {}\n".format(old_info))

        new_workspace_factory = "SDE"
        new_connection_info = {
            'authentication_mode': 'DBMS',
            'database': 'RTAA_MasterGDB',
            'db_connection_properties': r'RENO-GISWEB\SQLEXPRESS',
            'dbclient': 'sqlserver',
            'instance': 'sde:sqlserver:RENO-GISWEB\\SQLEXPRESS',
            'password': 'GIS@RTAA123!',
            'server': 'RENO-GISWEB',
            'user': 'GIS_Reader',
            'version': 'dbo.DEFAULT'
        }

        new_info = {
            "dataset": new_dataset[0],
            "workspace_factory": new_workspace_factory,
            "connection_info": new_connection_info
        }

        lyr.updateConnectionProperties(old_info, new_info)
        print(arcpy.GetMessages())
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
