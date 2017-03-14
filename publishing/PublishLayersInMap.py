import arcpy
from arcpy import mp
from copy import copy
import logging

"""For Testing"""
# p = mp.ArcGISProject(r"D:\ArcPro\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx")
# map = p.listMaps('LocalMap')[0]
# layers = [x for x in map.listLayers() if x.isFeatureLayer]
# layers = [x.name for x in layers]
map = arcpy.GetParameterAsText(0)
p = mp.ArcGISProject('current')
map = p.listMaps(map)[0]
layers = map.listLayers()
layers = arcpy.GetParameter(1)
layers = layers.exportToString().split(";")
arcpy.AddMessage("layers :: {}".format(layers))

toolbox_path = p.defaultToolbox
# Import the publishing toolbox
arcpy.AddToolbox(toolbox_path)

i = 0
for l in layers:
    lname = l.split("\\")[-1].replace("'", "")
    arcpy.AddMessage(lname)
    lyr = map.listLayers(lname)[0]
    if lyr.isFeatureLayer:
        arcpy.AddMessage("{} :: {}".format(lyr.name, lyr.longName))
        group_layer = lyr.longName.split("\\")[0]
        group_layer = " ".join([x.capitalize() for x in group_layer.split()])
        arcpy.AddMessage("{}. Map: {}".format(i, map.name))
        arcpy.AddMessage("{}. Group Layer: {}".format(i, group_layer))
        arcpy.AddMessage("{}. Layer Name: {}".format(i, lyr.name))
        clones = [copy(map.name), copy(group_layer), copy(l)]
        try:
            arcpy.PublishLayerToAGOL_RTAAPublishing(map.name, group_layer, lyr)
        except:
            arcpy.AddError("Input Parameters :: {}".format(clones))
        i += 1

