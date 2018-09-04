import arcpy
import os
from datetime import datetime
from arcpy import mp, env
from arcgisscripting import ExecuteError
import logging

env.preserveGlobalIds = True

home_dir = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(home_dir, 'logs')):
    os.mkdir(os.path.join(home_dir, 'logs'))

logging.basicConfig(filename=os.path.join(home_dir, 'logs/publish_layers.txt'))
logger = logging.getLogger(__name__)

# Test Parameters for Tool
# p = arcpy.mp.ArcGISProject(r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_Publishing\RTAA_publishing.aprx")
# map = 'Viewer_Local'
# m = p.listMaps("{}".format(map))[0]
# group_layer = 'Airfield'
# inlayer = 'Marking_Line'
# map_layer = m.listLayers(inlayer)[0]
# folder_name = 'Airfield'
# lyr_name = map_layer.name

try:
    p = mp.ArcGISProject('current')
    map = arcpy.GetParameterAsText(0)
    group_layer = arcpy.GetParameterAsText(1)
    map_layer = arcpy.GetParameter(2)
    folder_name = arcpy.GetParameterAsText(3)

    lyr_name = map_layer.name

    logger.info("lyr_name :: {}".format(lyr_name))
    m = p.listMaps("{}".format(map))[0]

    leaf_layer = lyr_name.split("\\")[-1]
    map_layer = m.listLayers(leaf_layer)[0]

    arcpy.AddMessage("Map: {}".format(m))

    output_folder = os.path.join(os.path.dirname(p.filePath), "scratch")
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Copy the dataSource from the enterpriseGDB to the project default GDB with the preserveGlobalIds env setting True
    # Add a new text field named src_GlobalID and populate that field with the Global ID for each feature

    env.workspace = output_folder

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

    credits = "Reno-Tahoe Airport Authority"
    arcpy.AddMessage("credits: {}".format(credits))

    use_limitations = "RTAA"
    arcpy.AddMessage("use_limitations: {}".format(use_limitations))

    p.save()

    # create a temp dataset using the group layer name
    dset = group_layer.replace(" ", "")
    out_dataset = "{}/{}".format(p.defaultGeodatabase, dset)
    if arcpy.Exists(out_dataset):
        arcpy.Delete_management(out_dataset)
    arcpy.CreateFeatureDataset_management(p.defaultGeodatabase, dset, arcpy.Describe(map_layer).spatialReference)
    # export the layer data source to the project defaultGDB
    out_fc = "{}/{}/{}".format(p.defaultGeodatabase, dset, map_layer.name.replace(" ", "_"))
    arcpy.Copy_management(map_layer.dataSource, out_fc)
    arcpy.AddField_management(out_fc, "src_GlobalID", "TEXT", "", "", 255)
    with arcpy.da.UpdateCursor(out_fc, ["GlobalID", "src_GlobalID"]) as cursor:
        for row in cursor:
            new_row = [row[0], row[0]]
            cursor.updateRow(new_row)

    # verify that the records were written
    missed_row = 0
    with arcpy.da.SearchCursor(out_fc, ["src_GlobalID"]) as cursor:
        for row in cursor:
            if not row[0]:
                missed_row += 1
    if missed_row:
        arcpy.AddError("{} src_GlobalIDs did not get populated".format(missed_row))
    else:
        old_connection_info = map_layer.connectionProperties
        new_connection_info = old_connection_info.copy()
        new_connection_info["workspace_factory"] = 'File Geodatabase'
        new_connection_info["connection_info"] = {
                'database': "{}".format(p.defaultGeodatabase)
            }
        # change the data source of the map layer to the exported feature class
        pre_path = "{}".format(map_layer.dataSource)
        try:
            map_layer.updateConnectionProperties(old_connection_info, new_connection_info)
        except Exception as e:
            print(e)
        print(arcpy.GetMessages())
        after_path = "{}".format(map_layer.dataSource)
        if pre_path != after_path:
            # m.getWebLayerSharingDraft("HOSTING SERVER", "FEATURE", inlayer, [map_layer])
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
                # TODO -Update the sharing on the service to put it in the Published Layers Group
            except Exception as e:
                arcpy.AddError(e)
        else:
            arcpy.AddError("Unable to updateConnectionProperties on Map Layer")

        # set the map layer back to the sde connection
        try:
            map_layer.updateConnectionProperties(new_connection_info, old_connection_info)
        except Exception as e:
            print(e)
        p.save()

except ExecuteError as e:
    logger.error(e)
    raise ExecuteError(e)



