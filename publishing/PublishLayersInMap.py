import arcpy
from arcpy import mp

"""For Testing"""
p = mp.ArcGISProject(r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\RTAA_publishing.aprx")
map = p.listMaps('LayerMap')[0]

# map = arcpy.GetParameterAsText(0)
# p = mp.ArcGISProject('current')
# map = p.listMaps(map)[0]

group_layers = ['Airspace', 'Navigation Aids', 'Restriction Zones', 'Structures', 'Airfield', 'Surface Transportation',
                'Cadastral', 'FEMA', 'Elevation']
group_layers.sort()

map_group_layers = []

toolbox_path = p.defaultToolbox
# Import the publishing toolbox
arcpy.AddToolbox(toolbox_path)

layers = map.listLayers()
for l in layers:
    if l.isGroupLayer:
        map_group_layers.append(l.name)
map_group_layers.sort()

if map_group_layers == group_layers:
    i = 0
    for l in layers:
        if l.isFeatureLayer:
            group_layer = l.longName.split("\\")[0]
            group_layer = " ".join([x.capitalize() for x in group_layer.split()])
            arcpy.AddMessage("{}. Map: {}".format(i, map.name))
            arcpy.AddMessage("{}. Group Layer: {}".format(i, group_layer))
            arcpy.AddMessage("{}. Layer Name: {}".format(i, l.name))

            arcpy.PublishLayerToAGOL_RTAAPublishing(map.name, group_layer, l)
            i += 1

else:
    arcpy.AddError("Current Group Layer Names: {}".format(map_group_layers))
    arcpy.AddError("These group names need to be fixed: {}".format([x for x in map_group_layers if x not in group_layers]))
    arcpy.AddError("Please rename the group layers to match these exactly. {}".format(
        [x for x in group_layers if x not in map_group_layers]))

