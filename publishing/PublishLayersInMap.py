import arcpy
from arcpy import mp
from copy import copy
import logging

"""For Testing"""
# p = mp.ArcGISProject(r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\RTAA_publishing.aprx")
# map = p.listMaps('LayerMap')[0]
# inlayers = [x for x in map.listLayers() if x.isFeatureLayer]
map = arcpy.GetParameterAsText(0)
p = mp.ArcGISProject('current')
map = p.listMaps(map)[0]
# layers = map.listLayers()
layers = arcpy.GetParameter(1)
arcpy.AddMessage("layers :: {}".format(layers))

toolbox_path = p.defaultToolbox
# Import the publishing toolbox
arcpy.AddToolbox(toolbox_path)

i = 0
for l in layers:
    if l.isFeatureLayer:
        layer = map.listLayers(l.name)[0]
        arcpy.AddMessage("{} :: {}".format(layer.name, layer.longName))
        group_layer = layer.longName.split("\\")[0]
        group_layer = " ".join([x.capitalize() for x in group_layer.split()])
        arcpy.AddMessage("{}. Map: {}".format(i, map.name))
        arcpy.AddMessage("{}. Group Layer: {}".format(i, group_layer))
        arcpy.AddMessage("{}. Layer Name: {}".format(i, layer.name))
        clones = [copy(map.name), copy(group_layer), copy(l)]
        try:
            arcpy.PublishLayerToAGOL_RTAAPublishing(map.name, group_layer, layer)
        except:
            arcpy.AddError("Input Parameters :: {}".format(clones))
        i += 1

