import arcpy
from arcpy import mp
import os

feature_layer_dir = arcpy.GetParameterAsText(0)
group_layer_dir = arcpy.GetParameterAsText(1)
local_map = arcpy.GetParameterAsText(2)

p = mp.ArcGISProject("CURRENT")
m = p.listMaps(local_map)[0]

p.save()


def save_layer(layer, out_dir):
    i = 0
    layer_name = layer.name.replace(" ", "_")
    for dirpath, dirs, files in os.walk(out_dir):
        for file in files:
            # all saved layer files have an underscore instead of spaces
            name = file.replace(".lyrx", "")
            if layer_name == name:
                save_path = os.path.join(dirpath, file)
                if not i:
                    os.remove(save_path)
                    # arcpy.SaveToLayerFile_management(l, save_path)
                    layer.saveACopy(save_path)
                    arcpy.AddMessage("Saved layer {} to file".format(name))
                    i += 1
                    break
                else:
                    arcpy.AddWarning("Layer {} has already been saved, check for duplicate layers".format(name))
    if not i:
        arcpy.AddError(
            "Unable to save layer file {}.  It must exist in the folder to be overwritten".format(layer_name))

if not os.path.exists(group_layer_dir):
    os.mkdir(group_layer_dir)

layers = m.listLayers()
for l in layers:
    if l.isFeatureLayer:
        out_folder = feature_layer_dir
        save_layer(layer=l, out_dir=out_folder)
    elif l.isGroupLayer:
        out_folder = group_layer_dir
        save_layer(layer=l, out_dir=out_folder)
    else:
        arcpy.AddMessage("Layer {} is not a feature layer or a group layer".format(l.name))



