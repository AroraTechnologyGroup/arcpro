import arcpy
import os
from datetime import datetime
from arcpy import mp, env


# determine folder name from the dataset that contains the feature class to be published
def get_folder_name(lyr):
    path = arcpy.Describe(lyr).path
    folder = path.split("\\")[-1]
    return folder

# Test Parameters for Tool
# p = arcpy.mp.ArcGISProject(r'C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\RTAA_publishing.aprx')
# m = p.listMaps()[0]
# layer = m.listLayers()[0]
# map_or_layers = layer

map = arcpy.GetParameterAsText(0)
group_layer = arcpy.GetParameterAsText(1)
layer = arcpy.GetParameterAsText(2)
#get layers that are sublayers or individual
layer = layer.split("\\")[-1]

p = mp.ArcGISProject('current')

# output_folder = r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\scratch"
output_folder = os.path.join(os.path.dirname(p.filePath), "scratch")
env.workspace = output_folder

m = p.listMaps("{}".format(map))[0]
arcpy.AddMessage("Map: {}".format(m))

# map_or_layers = m.listLayers("{}".format(arcpy.Describe(layer).name))[0]
map_or_layers = m.listLayers("{}".format(layer))[0]

arcpy.AddMessage("Layer: {}".format(map_or_layers.name))
arcpy.AddMessage("CatalogPath: {}".format(arcpy.Describe(map_or_layers).catalogPath))

out_sddraft = os.path.join(output_folder, "{}.sddraft".format(arcpy.Describe(map_or_layers).name))
arcpy.AddMessage("out_sddraft: {}".format(out_sddraft))

service_name = arcpy.Describe(map_or_layers).name.replace(" ", "_")
arcpy.AddMessage("service_name: {}".format(service_name))

server_type = "MY_HOSTED_SERVICES"
arcpy.AddMessage("server_type: {}".format(server_type))

service_type = "FEATURE_ACCESS"
arcpy.AddMessage("service_type: {}".format(service_type))

folder_name = get_folder_name(map_or_layers)
arcpy.AddMessage("folder_name: {}".format(folder_name))

overwrite_existing_service = True
arcpy.AddMessage("overwrite_existing_service: {}".format(overwrite_existing_service))

copy_data_to_server = True
arcpy.AddMessage("copy_data_to_server: {}".format(copy_data_to_server))

enable_editing = False
arcpy.AddMessage("enable_editing: {}".format(enable_editing))

allow_exporting = True
arcpy.AddMessage("allow_exporting: {}".format(allow_exporting))

enable_sync = False
arcpy.AddMessage("enable_sync: {}".format(enable_sync))

summary = "{} published on {}".format(service_name, datetime.ctime(datetime.today()))
arcpy.AddMessage("summary: {}".format(summary))

tags = ", ".join([folder_name, service_name])
arcpy.AddMessage("tags: {}".format(tags))

description = group_layer
arcpy.AddMessage("description: {}".format(description))

credits = "RTAA"
arcpy.AddMessage("credits: {}".format(credits))

use_limitations = "RTAA"
arcpy.AddMessage("use_limitations: {}".format(use_limitations))

p.save()
mp.CreateWebLayerSDDraft(map_or_layers=map_or_layers, out_sddraft=out_sddraft, service_name=service_name,
                         server_type=server_type, service_type=service_type, folder_name=folder_name,
                         overwrite_existing_service=overwrite_existing_service, copy_data_to_server=copy_data_to_server,
                         enable_editing=enable_editing, allow_exporting=allow_exporting, enable_sync=enable_sync,
                         summary=summary, tags=tags, description=description, credits=credits,
                         use_limitations=use_limitations)

definition = out_sddraft.replace(".sddraft", ".sd")
arcpy.StageService_server(out_sddraft, definition)
arcpy.UploadServiceDefinition_server(definition, 'My Hosted Services')




