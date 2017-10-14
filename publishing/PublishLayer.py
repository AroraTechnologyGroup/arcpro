import arcpy
import os
from datetime import datetime
from arcpy import mp, env
from arcgisscripting import ExecuteError
import logging

home_dir = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(home_dir, 'logs')):
    os.mkdir(os.path.join(home_dir, 'logs'))

logging.basicConfig(filename=os.path.join(home_dir, 'logs/publish_layers.txt'))
logger = logging.getLogger(__name__)


# determine MyContent folder name from the group layer that contains the feature class to be published
def get_folder_name(lyr):
    path = arcpy.Describe(lyr).path
    folder = path.split("\\")[-1]
    return folder

# Test Parameters for Tool
# p = arcpy.mp.ArcGISProject(r'D:\ArcPro\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx')
# map = 'LocalMap'
# m = p.listMaps("{}".format(map))[0]
# group_layer = 'Airspace'
# inlayer = 'PRIM77'
# map_layer = m.listLayers(inlayer)[0]
# lyr_name = map_layer.name

try:
    p = mp.ArcGISProject('current')
    map = arcpy.GetParameterAsText(0)
    group_layer = arcpy.GetParameterAsText(1)
    map_layer = arcpy.GetParameter(2)
    lyr_name = map_layer.name

    logger.warning("lyr_name :: {}".format(lyr_name))
    m = p.listMaps("{}".format(map))[0]

    leaf_layer = lyr_name.split("\\")[-1]
    map_layer = m.listLayers(leaf_layer)[0]

    arcpy.AddMessage("Map: {}".format(m))

    output_folder = os.path.join(os.path.dirname(p.filePath), "scratch")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    env.workspace = output_folder

    arcpy.AddMessage("Tests : {}".format(",".join([x.name for x in m.listLayers() if x.isFeatureLayer])))

    arcpy.AddMessage("groupLayer :: {}".format(group_layer))

    # arcpy.AddMessage("Layer: {}".format(lyr_name))
    arcpy.AddMessage("CatalogPath: {}".format(arcpy.Describe(map_layer).catalogPath))

    out_sddraft = os.path.join(output_folder, "{}.sddraft".format(leaf_layer.replace(" ", "_")))
    if os.path.exists(out_sddraft):
        os.remove(out_sddraft)
    arcpy.AddMessage("out_sddraft: {}".format(out_sddraft))

    arcpy.AddMessage("service_name: {}".format(leaf_layer))

    server_type = "MY_HOSTED_SERVICES"
    arcpy.AddMessage("server_type: {}".format(server_type))

    service_type = "FEATURE_ACCESS"
    arcpy.AddMessage("service_type: {}".format(service_type))

    folder_name = get_folder_name(map_layer)
    logging.info(folder_name)
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

    summary = "{} published on {}".format(lyr_name, datetime.ctime(datetime.today()))
    arcpy.AddMessage("summary: {}".format(summary))

    tags = ", ".join([folder_name, leaf_layer])
    arcpy.AddMessage("tags: {}".format(tags))

    description = group_layer
    arcpy.AddMessage("description: {}".format(description))

    credits = "RTAA"
    arcpy.AddMessage("credits: {}".format(credits))

    use_limitations = "RTAA"
    arcpy.AddMessage("use_limitations: {}".format(use_limitations))

    p.save()
    mp.CreateWebLayerSDDraft(map_or_layers=map_layer, out_sddraft=out_sddraft, service_name=leaf_layer,
                             server_type=server_type, service_type=service_type, folder_name=folder_name,
                             overwrite_existing_service=overwrite_existing_service, copy_data_to_server=copy_data_to_server,
                             enable_editing=enable_editing, allow_exporting=allow_exporting, enable_sync=enable_sync,
                             summary=summary, tags=tags, description=description, credits=credits,
                             use_limitations=use_limitations)

    definition = out_sddraft.replace(".sddraft", ".sd")
    if os.path.exists(definition):
        os.remove(definition)

    try:
        arcpy.StageService_server(out_sddraft, definition)
    except Exception as e:
        arcpy.AddError(e)

    try:
        arcpy.UploadServiceDefinition_server(definition, 'My Hosted Services')
    except Exception as e:
        arcpy.AddError(e)

except ExecuteError as e:
    logger.error(e)
    raise ExecuteError(e)



