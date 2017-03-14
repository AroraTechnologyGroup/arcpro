import arcpy
import os
from arcpy import mp

project_path = r"D:\ArcPro\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx"
if not os.path.exists(project_path):
    project_path = arcpy.GetParameterAsText(0)

project = mp.ArcGISProject(project_path)

layer_dir = r"D:\ArcPro\RTAA_Printing_Publishing\FeatureLayers"
if not os.path.exists(layer_dir):
    layer_dir = arcpy.GetParameterAsText(1)

local_map = project.listMaps("LocalMap")[0]
flayers = [x for x in local_map.listLayers() if x.isFeatureLayer]

for lyr in flayers:
    name = lyr.name.split("\\")[-1]
    for root, dirs, files in os.walk(layer_dir):
        for file in files:
            base = file.replace(".lyrx", "")
            base = base.replace("_", " ")
            if name == base:
                if file.endswith(".lyrx"):
                    layer_file = mp.LayerFile(os.path.join(root, file))
                    local_map.insertLayer(lyr, layer_file, 'AFTER')
                    local_map.removeLayer(lyr)
                    arcpy.AddMessage("{} replaced".format(base))

flayers = [x for x in local_map.listLayers() if x.isFeatureLayer]
for fly in flayers:
    fly.visible = True

project.save()
