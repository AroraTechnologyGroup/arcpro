import arcpy
from arcpy import mp
import os
import shutil
import sys
import subprocess
from subprocess import PIPE
import json
from repairMapLayers import LayerRepairTool
import logging
from arcpy import Extent
import argparse

home_dir = os.path.dirname(os.path.abspath(__file__))
media_dir = r"C:/Users/rich/PycharmProjects/rtaa_gis/rtaa_gis/media"
if not os.path.exists(media_dir):
    media_dir = r"C:\GitHub\rtaa_gis\rtaa_gis\media"

gdb_path = r"G:\GIS Data\Arora\rtaa\MasterGDB_05_25_16\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
if not os.path.exists(gdb_path):
    gdb_path = r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"

default_project = r"G:\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"
if not os.path.exists(default_project):
    default_project = r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"

layer_dir = r"G:\GIS Data\Arora\rtaa\layers"
if not os.path.exists(layer_dir):
    layer_dir = r"C:\ESRI_WORK_FOLDER\rtaa\layers"

page_title = r"RTAA Airport Authority Test Print"


class ArcProPrint:
    def __init__(self, username, webmap_as_json):
        self.username = username
        self.webmap = json.loads(webmap_as_json)

    def stage_project(self):
        out_dir = os.path.join(media_dir, self.username)
        if not os.path.exists(out_dir):
            os.chdir(media_dir)
            os.mkdir(self.username)
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
            lrp = LayerRepairTool(default_project)
            # returns project with layers saved in map copied to media
            aprx = lrp.repair(target_gdb=gdb_path)

            # copy_project = shutil.copy2(default_project, out_dir)
            aprx.saveACopy(os.path.join(out_dir, "rtaa-print.aprx"))
            os.chdir(out_dir)
            project = mp.ArcGISProject("rtaa-print.aprx")

            return project

    def print_page(self, page_title):
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
        for root, dirs, files in os.walk(layer_dir):
            for file in files:
                if file.endswith(".lyrx"):
                    filename = file.replace(".lyrx", "").replace(" ", "").lower()
                    if filename in add_layers:
                        layer_path = os.path.join(root, file)
                        lf = mp.LayerFile(layer_path)
                        lf.opacity = visible_layers[filename]["opacity"]
                        map.addLayer(lf, "TOP")

        # Export Layout to PDF
        aprx.save()
        output_pdf = os.path.join(media_dir, "{}/layout.pdf".format(self.username))
        if os.path.exists(output_pdf):
            os.remove(output_pdf)

        lyt.exportToPDF(output_pdf, 300, "FASTER", layers_attributes="LAYERS_AND_ATTRIBUTES")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-username', help='the username attached to the request')
    parser.add_argument('-media', help='the file path to the django media folder')
    args = parser.parse_args()

    username = args.username
    media_dir = args.media

    home = os.path.join(media_dir, username)
    web_map_file = os.path.join(home, 'webmap.json')
    web_map = open(web_map_file, 'r')
    p = ArcProPrint(username, web_map.read())
    p.print_page(page_title)
