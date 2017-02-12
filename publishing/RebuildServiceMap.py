import arcpy
from arcpy import mp
import os

p = mp.ArcGISProject(r'C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\RTAA_publishing.aprx')
map = p.listMaps('ServiceMap')[0]
layers = map.listLayers()
group_layers = []
feature_layers = []
for l in layers:
    if l.isGroupLayer:
        group_layers.append(l.name)
    if l.isFeatureLayer:
        feature_layers.append(l.name)

web_layers = [x for x in group_layers if x in feature_layers]



