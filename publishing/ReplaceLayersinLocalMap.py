import arcpy
import os
from arcpy import mp

"""
Use this tool to replace the layers in the local map with the stored layers files

1.  After layer symbology has been saved from AGOL
2.  Run this tool from within the Pro Project

"""

project = mp.ArcGISProject("CURRENT")

layer_dir = arcpy.GetParameterAsText(0)

local_map = arcpy.GetParameterAsText(1)

local_map = project.listMaps(local_map)[0]

flayers = [x for x in local_map.listLayers() if x.isFeatureLayer]
# get the names for each feature layer in the local map

for lyr in flayers:
    name = lyr.name.split("\\")[-1]
    for root, dirs, files in os.walk(layer_dir):
        for file in files:
            base = file.replace(".lyrx", "")
            # no layers in the map have underscores
            base = base.replace("_", " ")
            # map layer name equals layer files name (after formatting)
            if name == base:
                if file.endswith(".lyrx"):
                    # creating layer file from saved layer
                    layer_file = mp.LayerFile(os.path.join(root, file))
                    local_map.insertLayer(lyr, layer_file, 'AFTER')
                    local_map.removeLayer(lyr)
                    arcpy.AddMessage("{} replaced".format(base))

flayers = [x for x in local_map.listLayers() if x.isFeatureLayer]
for fly in flayers:
    # ensure that all feature layers are visible
    fly.visible = True

project.save()
