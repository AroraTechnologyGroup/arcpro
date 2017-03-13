import arcpy
from arcpy import mp
import os

layer_mappings = {
    "RunwayHelipadDesignSurface": ["BRL", "OTHER", "ROFA", "IOFZ", "POFZ", "OFZ",
                                      "RPZ", "TOFA", "TSA", "TSS"],
    "ObstructionIdSurface": ["APRC77", "PRIM77", "TRNS77", "OEIA", "HORZ_77"]
}

out_folder = arcpy.GetParameterAsText(0)
# out_folder = r"D:\ArcPro\RTAA_Printing_Publishing\FeatureLayers"
map_name = arcpy.GetParameterAsText(1)
# map_name = "ViewerMap_2_26_B"
source_gdb = arcpy.GetParameterAsText(2)
# source_gdb = r"D:\EsriGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
# """For Testing"""
# p = mp.ArcGISProject(r"D:\ArcPro\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx")
p = mp.ArcGISProject('current')
p.save()
m = p.listMaps(map_name)[0]
flayers = [x for x in m.listLayers() if x.isFeatureLayer]
for lyr in flayers:

    layer_name = lyr.name.split("\\")[-1].replace(" ", "_")
    old_info = lyr.connectionProperties

    i = 0
    new_dataset = []
    for k, v in layer_mappings.items():
        if layer_name in v:
            new_dataset.append(k)
            i += 1
            break

    if not i:
        new_dataset.append(lyr.name.replace("_", ""))

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