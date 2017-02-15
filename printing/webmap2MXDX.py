import arcpy
from arcpy import mp
import os
import shutil
import sys
import subprocess
from subprocess import PIPE
import json
import logging
from arcpy import Extent
import argparse

home_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(home_dir)
from repairMapLayers import LayerRepairTool

username = "rhughes"

# home pc
media_dir = r"C:/Users/rich/PycharmProjects/rtaa_gis/rtaa_gis/media"
if not os.path.exists(media_dir):
    # work laptop
    media_dir = r"C:\GitHub\rtaa_gis\rtaa_gis\media"
if not os.path.exists(media_dir):
    # azure staging
    media_dir = r"C:\inetpub\django_staging\rtaa_gis\rtaa_gis\media"

# home pc
gdb_path = r"G:\GIS Data\Arora\rtaa\MasterGDB_05_25_16\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
if not os.path.exists(gdb_path):
    # work laptop
    gdb_path = r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
if not os.path.exists(gdb_path):
    # azure staging
    gdb_path = r"C:\inetpub\rtaa_gis_data\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"

# home pc
default_project = r"G:\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"
if not os.path.exists(default_project):
    # work laptop
    default_project = r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"
if not os.path.exists(default_project):
    # azure staging
    default_project = r"C:\inetpub\rtaa_gis_data\RTAA_Printing.aprx"

# home pc
layer_dir = r"G:\GIS Data\Arora\rtaa\layers"
if not os.path.exists(layer_dir):
    # work laptop
    layer_dir = r"C:\ESRI_WORK_FOLDER\rtaa\layers"
if not os.path.exists(layer_dir):
    # azure staging
    layer_dir = r"C:\inetpub\rtaa_gis_data\layers"

webmap_file = os.path.join(home_dir, "printing/tests/fixtures/webmap.json")
webmap = open(webmap_file, 'r').read()
page_title = r"RTAA Airport Authority Test Print"


class ArcProPrint:
    def __init__(self, username, media, webmap_as_json, gdbPath, defaultProject, layerDir):
        self.username = username
        self.media_dir = media
        self.webmap = json.loads(webmap_as_json)
        self.gdb_path = gdbPath
        self.default_project = defaultProject
        self.layer_dir = layerDir

    def stage_project(self):
        try:
            out_dir = os.path.join(self.media_dir, self.username)
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
            os.chdir(out_dir)

            project_file = []
            for file in os.listdir(out_dir):
                name, extension = os.path.splitext(file)
                if extension == ".aprx":
                    project_file.append(os.path.join(out_dir, file))
                    break
            if len(project_file):
                project = arcpy.mp.ArcGISProject(project_file[0])
                return project
            else:
                # repair any broken layers before copying project
                lrp = LayerRepairTool(self.default_project)
                # returns project saved with layers saved map
                aprx = lrp.repair(target_gdb=self.gdb_path)

                # copy_project = shutil.copy2(default_project, out_dir)
                aprx.saveACopy(os.path.join(out_dir, "rtaa-print.aprx"))
                os.chdir(out_dir)
                project = mp.ArcGISProject("rtaa-print.aprx")
                return project
        except:
            print(sys.exc_traceback())

    def print_page(self, page_title):
        out_dir = os.path.join(self.media_dir, self.username)
        aprx = self.stage_project()
        map = aprx.listMaps("Map")[0]
        broken_layers = map.listBrokenDataSources()
        for l in broken_layers:
            try:
                print("connectionProperties: {}".format(l.connectionProperties))

                conProp = l.connectionProperties
                conProp['connection_info']['database'] = gdb_path
                l.connectionProperties = conProp
            except TypeError:
                pass
        aprx.save()

        visible_layers = {}
        op_layers = self.webmap["operationalLayers"]
        map_options = self.webmap["mapOptions"]

        # Get the extent from the web map and project the center point into State Plane
        e = map_options["extent"]
        spatial_ref = e["spatialReference"]["wkid"]
        middle_point = arcpy.Point((e["xmax"]+e["xmin"])/2, (e["ymax"]+e["ymin"])/2)
        old_sr = arcpy.SpatialReference(spatial_ref)
        middle_geo = arcpy.PointGeometry(middle_point, old_sr)
        new_sr = arcpy.SpatialReference(6523)
        proj_point = middle_geo.projectAs(new_sr)
        cam_X = proj_point.firstPoint.X
        cam_Y = proj_point.firstPoint.Y
        scale = map_options["scale"]

        # TODO-Set Text Element properties of the Layout
        lyt = aprx.listLayouts("Layout")[0]
        title = lyt.listElements("TEXT_ELEMENT", "TITLE")[0]
        title.text = page_title

        # TODO-Set the Map Frame properties (including the Camera)
        map_frame = lyt.listElements("MAPFRAME_ELEMENT")[0]
        camera = map_frame.camera
        camera.scale = scale
        camera.X = cam_X
        camera.Y = cam_Y
        aprx.save()

        # TODO-Add Layers for each visible layer in webmap json to the map; set opacity
        for x in op_layers:
            try:
                draw_order = op_layers.index(x)
                service_name = x["title"]
                if draw_order == 0:
                    # set to basemap gallery title
                    title = x["title"]
                else:
                    title = x["title"].replace(" ", "").lower()
                opacity = x["opacity"]
                url = x["url"]
                if title not in visible_layers.keys():
                    visible_layers[title] = {}

                visible_layers[title]["opacity"] = opacity
                visible_layers[title]["draw_order"] = draw_order
                visible_layers[title]["service_name"] = service_name
                visible_layers[title]["url"] = url
            except KeyError as e:
                pass

        source_layers = map.listLayers()
        existing_layers = {}
        for x in source_layers:
            formatted_name = x.name.replace(" ", "").lower()
            existing_layers[formatted_name] = x.name

        rem_layers = [x for x in existing_layers.keys() if x not in visible_layers.keys()]
        for lyr in rem_layers:
            try:
                del_lyr = map.listLayers("{}".format(existing_layers[lyr]))[0]
                map.removeLayer(del_lyr)
            except IndexError:
                pass

        add_layers = [x for x in visible_layers.keys() if x not in existing_layers.keys()]
        for x in add_layers:
            if visible_layers[x]["draw_order"] == 0:
                map.addDataFromPath(visible_layers[x]["url"])
                pass
        for root, dirs, files in os.walk(self.layer_dir):
            for file in files:
                if file.endswith(".lyrx"):
                    filename = file.replace(".lyrx", "").replace(" ", "").lower()
                    if filename in add_layers:
                        layer_path = os.path.join(root, file)
                        lf = mp.LayerFile(layer_path)
                        lf.opacity = visible_layers[filename]["opacity"]
                        map.addLayer(lf, "BOTTOM")

        # Export Layout to PDF
        aprx.save()
        output_pdf = "{}/layout.pdf".format(out_dir)
        if os.path.exists(output_pdf):
            os.remove(output_pdf)

        try:
            lyt.exportToPDF(output_pdf, 300, "FASTER", layers_attributes="LAYERS_AND_ATTRIBUTES")
        except:
            print(sys.exc_traceback())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-username', help='the username attached to the request')
    parser.add_argument('-media', help='the file path to the django media folder')
    parser.add_argument('-gdbPath', help="use the catalog Path to the master GDB")
    parser.add_argument('-defaultProject', help="use the path to the parent arcpro project")
    parser.add_argument('-layerDir', help="the parent directory storing each datasets layer files")
    args = parser.parse_args()

    if args.username is not None:
        username = args.username
    if args.media is not None:
        media_dir = args.media
    if args.gdbPath is not None:
        gdb_path = args.gdbPath
    if args.defaultProject is not None:
        default_project = args.defaultProject
    if args.layerDir is not None:
        layer_dir = args.layerDir

    home = os.path.join(media_dir, username)
    web_map_file = os.path.join(home, 'webmap.json')
    if os.path.exists(web_map_file):
        webmap = open(web_map_file, 'r').read()
    try:
        p = ArcProPrint(username, media_dir, webmap, gdb_path, default_project, layer_dir)
        p.print_page(page_title)
    except:
        print(sys.exc_traceback())
