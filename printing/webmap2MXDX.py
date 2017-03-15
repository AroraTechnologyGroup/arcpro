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
import traceback

home_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(home_dir)
from repairMapLayers import LayerRepairTool

username = "gissetup"

environ = "staging"


media_dir = {
    "home": "C:/Users/rich/PycharmProjects/rtaa_gis/rtaa_gis/media",
    "work": "C:/GitHub/rtaa_gis/rtaa_gis/media",
    "staging": "C:/inetpub/django_staging/rtaa_gis/rtaa_gis/media",
    "production": "C:/inetpub/django_prod/rtaa_gis/rtaa_gis/media",
}
media_dir = media_dir[environ]

gdb_path = {
    "home": r"G:\GIS Data\Arora\rtaa\MasterGDB_05_25_16\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb",
    "work": r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb",
    "staging": r"C:\inetpub\rtaa_gis_data\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb",
    "production": r"C:\inetpub\rtaa_gis_data\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
}
gdb_path = gdb_path[environ]

default_project = {
    "home": r"G:\Documents\ArcGIS\Projects\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx",
    "work": r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx",
    "staging": r"C:\inetpub\rtaa_gis_data\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx",
    "production": r"C:\inetpub\rtaa_gis_data\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx"
}
default_project = default_project[environ]

layer_dir = {
    "home": r"G:\GIS Data\Arora\rtaa\layers",
    "work": r"C:\ESRI_WORK_FOLDER\rtaa\layers",
    "staging": r"C:\inetpub\rtaa_gis_data\RTAA_Printing_Publishing\FeatureLayers",
    "production": r"C:\inetpub\rtaa_gis_data\RTAA_Printing_Publishing\FeatureLayers"
}
layer_dir = layer_dir[environ]

layout_name = "11_17_landscape"
map_title = "RTAA GIS Map"

web_map_file = os.path.join(home_dir, "printing/tests/fixtures/webmap.json")
webmap = open(web_map_file, 'r').read()

page_title = r"RTAA Airport Authority Test Print"


class ArcProPrint:
    def __init__(self, username, media, webmap_as_json, gdbPath, defaultProject, layerDir, layout):
        self.username = username
        self.media_dir = media
        self.webmap = json.loads(webmap_as_json)
        self.gdb_path = gdbPath
        self.default_project = defaultProject
        self.layer_dir = layerDir
        self.layout = layout

    def stage_project(self):
        try:
            out_dir = os.path.join(self.media_dir, self.username)
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
            out_dir = os.path.join(out_dir, 'prints')
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
                return project_file[0]
            else:
                # repair any broken layers before copying project
                lrp = LayerRepairTool(self.default_project)
                # returns project saved with layers saved in map
                aprx = lrp.repair(target_gdb=self.gdb_path)

                # copy_project = shutil.copy2(default_project, out_dir)
                aprx.saveACopy(os.path.join(out_dir, "rtaa-print.aprx"))
                return os.path.join(out_dir, "rtaa-print.aprx")

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(traceback.print_tb(exc_traceback))

    def print_page(self):
        out_dir = os.path.join(self.media_dir, self.username)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        out_dir = os.path.join(out_dir, 'prints')
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        aprx_path = self.stage_project()
        aprx = mp.ArcGISProject(aprx_path)
        map = aprx.listMaps("LocalMap")[0]
        broken_layers = [x for x in map.listBrokenDataSources() if x.isFeatureLayer]
        if len(broken_layers):
            lrp = LayerRepairTool(aprx_path)
            # returns project saved with layers saved in map
            aprx = lrp.repair(target_gdb=self.gdb_path)

        visible_layers = {}
        op_layers = self.webmap["operationalLayers"][1:]
        map_options = self.webmap["mapOptions"]

        # Get the extent from the web map and project the center point into State Plane
        e = map_options["extent"]
        spatial_ref = e["spatialReference"]["wkid"]
        middle_point = arcpy.Point((e["xmax"]+e["xmin"])/2.0, (e["ymax"]+e["ymin"])/2.0)
        # lower_left = arcpy.Point(e["xmin"], e["ymin"])
        # upper_right = arcpy.Point(e["xmax"], e["ymax"])
        old_sr = arcpy.SpatialReference(spatial_ref)
        middle_geo = arcpy.PointGeometry(middle_point, old_sr)
        # ll_geo = arcpy.PointGeometry(lower_left, old_sr)
        # ur_geo = arcpy.PointGeometry(upper_right, old_sr)

        new_sr = arcpy.SpatialReference(6523)
        proj_mid_json = middle_geo.projectAs(new_sr)
        proj_mid_json = proj_mid_json.JSON
        proj_mid = json.loads(proj_mid_json)

        # proj_ll_json = ll_geo.projectAs(new_sr)
        # proj_ll_json = proj_ll_json.JSON
        # proj_ll = json.loads(proj_ll_json)
        #
        # proj_ur_json = ur_geo.projectAs(new_sr)
        # proj_ur_json = proj_ur_json.JSON
        # proj_ur = json.loads(proj_ur_json)

        # new_extent = arcpy.Extent(proj_ll["x"], proj_ll["y"], proj_ur["x"], proj_ur["y"])
        cam_X = proj_mid["x"]
        cam_Y = proj_mid["y"]
        scale = map_options["scale"]

        # TODO-Set Text Element properties of the Layout
        lyt = aprx.listLayouts(self.layout)[0]
        title = lyt.listElements("TEXT_ELEMENT", "TITLE")[0]
        title.text = "BETA - Viewer Map Print"

        # TODO-Set the Map Frame properties (including the Camera)
        map_frame = lyt.listElements("MAPFRAME_ELEMENT")[0]
        camera = map_frame.camera
        camera.scale = scale
        camera.X = float(cam_X)
        camera.Y = float(cam_Y)
        # TODO-build an Extent and set to Camera

        aprx.save()

        op_layers = [x for x in op_layers if x["id"] not in ['labels', 'map_graphics']]

        # TODO-Add Layers for each visible layer in webmap json to the map; set opacity
        for x in op_layers:
            try:
                draw_order = op_layers.index(x)
                service_name = x["title"]
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
            if x.isFeatureLayer:
                formatted_name = x.name.replace(" ", "").lower()
            else:
                formatted_name = x.name
            existing_layers[formatted_name] = x
            if formatted_name not in visible_layers.keys():
                try:
                    if x.isFeatureLayer:
                        map.removeLayer(x)
                        pass
                    elif x.isGroupLayer:
                        pass
                    elif x.isRasterLayer:
                        # mxdx.removeLayer(x)
                        pass
                    elif x.isWebLayer:
                        pass
                    pass
                except IndexError:
                    pass

        add_layers = [x for x in visible_layers.keys() if x not in existing_layers.keys()]
        for root, dirs, files in os.walk(self.layer_dir):
            for file in files:
                if file.endswith(".lyrx"):
                    filename = file.replace(".lyrx", "").replace(" ", "").lower()
                    if filename in add_layers:
                        layer_path = os.path.join(root, file)
                        lf = mp.LayerFile(layer_path)
                        lf.opacity = visible_layers[filename]["opacity"]
                        draw_order = visible_layers[filename]["draw_order"]
                        lyrs = map.listLayers()
                        if draw_order >= len(lyrs):
                            map.addLayer(lf, "TOP")
                        else:
                            map.insertLayer(lyrs[draw_order], lf, "BEFORE")

        # camera.setExtent(new_extent)
        # map_frame.panToExtent(new_extent)

        # Reorder Layers and set opacity
        source_layers = self.reorder_layers(map, visible_layers)

        aprx.save()

        i = True
        num = 1
        os.chdir(out_dir)
        output_pdf = "map_print.pdf"
        while i:
            if os.path.exists(output_pdf):
                output_pdf = "map_print{}.pdf".format(num)
                num += 1
            else:
                i = False

        try:
            lyt.exportToPDF(output_pdf, 300, "FASTER", layers_attributes="LAYERS_AND_ATTRIBUTES")
            print(output_pdf)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print(sys.exc_traceback(exc_traceback))
            return

    @staticmethod
    def reorder_layers(mxdx, op_layers):
        all_layers = mxdx.listLayers()
        for layer in all_layers:
            if layer.isWebLayer:
                layer.transparency = 100

        source_layers = [x for x in all_layers if x.isFeatureLayer]
        for x in source_layers:
            try:
                formatted_name = x.name.replace(" ", "").lower()

                try:
                    opacity = op_layers[formatted_name]["opacity"]
                    x.transparency = opacity * 100
                except KeyError as e:
                    pass

                draw_order = op_layers[formatted_name]["draw_order"]
                mxdx.moveLayer(all_layers[draw_order], x, "BEFORE")

            except IndexError:
                pass

        source_layers = mxdx.listLayers()
        return source_layers

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-username', help='the username attached to the request')
    parser.add_argument('-media', help='the file path to the django media folder')
    parser.add_argument('-gdbPath', help="use the catalog Path to the master GDB")
    parser.add_argument('-defaultProject', help="use the path to the parent arcpro project")
    parser.add_argument('-layerDir', help="the parent directory storing each datasets layer files")
    parser.add_argument('-layout', help="choose the layout to print")

    args = parser.parse_args()

    if args.username is not None:
        username = args.username
    if args.media is not None:
        media_dir = args.media
        home = os.path.join(media_dir, username)
        web_map_file = os.path.join(home, 'prints/webmap.json')
        if os.path.exists(web_map_file):
            webmap = open(web_map_file, 'r').read()
    if args.gdbPath is not None:
        gdb_path = args.gdbPath
    if args.defaultProject is not None:
        default_project = args.defaultProject
    if args.layerDir is not None:
        layer_dir = args.layerDir
    if args.layout is not None:
        layout_name = args.layout

    try:
        p = ArcProPrint(username, media_dir, webmap, gdb_path, default_project, layer_dir, layout_name)
        p.print_page()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(traceback.print_tb(exc_traceback))
