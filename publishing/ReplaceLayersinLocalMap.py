import arcpy
import os
from arcpy import mp

project = mp.ArcGISProject("CURRENT")

layer_dir = arcpy.GetParameterAsText(0)

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
