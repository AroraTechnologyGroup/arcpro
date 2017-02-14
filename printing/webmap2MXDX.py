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


home_dir = os.path.dirname(os.path.abspath(__file__))
media_dir = r"C:/Users/rich/PycharmProjects/rtaa_gis/rtaa_gis/media"
gdb_path = r"G:\GIS Data\Arora\rtaa\MasterGDB_05_25_16\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
username = "rhughes@aroraengineers.com"
default_project = r"G:\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"
layer_dir = r"G:\GIS Data\Arora\rtaa\layers"
webmap = open(os.path.join(home_dir, 'tests/fixtures/webmap.json'), 'r')
page_title = r"RTAA Airport Authority Test Print"


class ArcProPrint:
    def __init__(self, username, webmap):
        self.username = username
        self.webmap = webmap

    def stage_project(self):
        out_dir = os.path.join(media_dir, self.username)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        os.chdir(out_dir)

        project_file = []
        for file in os.listdir(out_dir):
            if file.endswith(".aprx"):
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

        # TODO-Set style and properties of the Layout
        lyt = aprx.listLayouts("Layout")[0]
        title = lyt.listElements("TEXT_ELEMENT", "TITLE")[0]
        title.text = page_title

        # TODO-Add Layers for each visible layer in webmap json; set opacity
        visible_layers = {}
        webmap = json.loads(self.webmap)
        op_layers = webmap["operationalLayers"]

        for x in op_layers:
            try:
                draw_order = op_layers.index(x)
                title = x["title"].replace(" ", "").lower()
                opacity = x["opacity"]
                if title in visible_layers.keys():
                    if type(visible_layers[title]) == "DictType":
                        visible_layers[title]["opacity"] = opacity
                        visible_layers[title]["draw_order"] = draw_order
                    else:
                        raise Exception("set layer value as Dict.")
                else:
                    visible_layers[title] = {}
                    visible_layers[title]["opacity"] = opacity
                    visible_layers[title]["draw_order"] = draw_order
            except KeyError as e:
                pass

        source_layers = map.listLayers()
        existing_layers = [x.name.replace(" ", "").lower() for x in source_layers]
        rem_layers = [x for x in existing_layers if x not in visible_layers.keys()]
        for lyr in rem_layers:
            del_lyr = map.listLayers("{}".format(lyr))[0]
            map.removeLayer(del_lyr)

        add_layers = [x for x in visible_layers.keys() if x not in existing_layers]
        for root, dirs, files in os.walk(layer_dir):
            for file in files:
                if file.endswith(".lyrx"):
                    filename = file.replace(".lyrx", "").replace(" ", "").lower()
                    if filename in add_layers:
                        layer_path = os.path.join(root, file)
                        lf = mp.LayerFile(layer_path)
                        lf.opacity = visible_layers[filename]["opacity"]
                        order = visible_layers[filename]["draw_order"]

                        if order == 0:
                            # TODO-Set Basemap in aprx to match the webmap
                            pass
                        else:
                            map.addLayer(lf, order)




        # Export Layout to PDF
        aprx.save()
        output_pdf = os.path.join(media_dir, "{}/layout.pdf".format(self.username))
        if os.path.exists(output_pdf):
            os.remove(output_pdf)

        lyt.exportToPDF(output_pdf, 300, "FASTER", layers_attributes="LAYERS_AND_ATTRIBUTES")


if __name__ == "__main__":
    p = ArcProPrint(username, webmap.read())
    p.print_page(page_title)
