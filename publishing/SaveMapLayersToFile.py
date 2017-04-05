import arcpy
from arcpy import mp
import os

# Set the outfolder to be the FeatureLayer and GroupLayer directory
feature_layer_dir = arcpy.GetParameterAsText(0)
group_layer_dir = arcpy.GetParameterAsText(1)

p = mp.ArcGISProject("CURRENT")
m = p.listMaps("LocalMap")[0]

# """For Testing"""
# p = mp.ArcGISProject(r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\RTAA_publishing.aprx")
# m = p.listMaps('LayerMap')[0]

p.save()


def save_layer(layer, out_dir):
    layer_name = layer.name.replace(" ", "_")
    i = 0
    for dirpath, dirs, files in os.walk(out_dir):
        for file in files:
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



