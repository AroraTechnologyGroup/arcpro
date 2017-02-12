import arcpy
from arcpy import mp
import os
import sys
import subprocess
from subprocess import PIPE
import json

home_dir = os.path.dirname(os.path.abspath(__file__))
media_dir = r"C:/Users/rich/PycharmProjects/rtaa_gis/rtaa_gis/media"


class ArcProPrint:
    def __init__(self, webmap, layerDir, project):
        self.webmap_json = webmap
        self.layer_dir = layerDir
        self.project = project

    def print_page(self, page_title):
        aprx = mp.ArcGISProject(self.project)
        map = aprx.listMaps("Map")[0]

        lyt = aprx.listLayouts("Layout")[0]
        title = lyt.listElements("TEXT_ELEMENT", "TITLE")[0]
        title.text = page_title

        # TODO-Add Layers for each visible layer in webmap json; set opacity
        visible_layers = []
        webmap = json.loads(self.webmap_json)
        op_layers = webmap["operationalLayers"]

        for x in op_layers:
            # title = x["title"]
            # opacity = x["opacity"]
            visible_layers.append(x)

        os.chdir(self.layer_dir)
        for root, dirs, files in os.walk(layer_dir):
            for file in files:
                if file.endswith(".lyrx"):
                    layer_path = os.path.join(root, file)
                    lf = mp.LayerFile(layer_path)
                    map.addLayer(lf)

        # TODO-Set Basemap in aprx to match the webmap

        # Export Layout to PDF
        aprx.save()
        output_pdf = os.path.join(home_dir, "tests/output/layout.pdf")
        if os.path.exists(output_pdf):
            os.remove(output_pdf)

        lyt.exportToPDF(output_pdf, 300, "BEST")


if __name__ == "__main__":

    webmap = open(os.path.join(home_dir, 'tests/fixtures/webmap.json'), 'r')

    layer_dir = r"G:\GIS Data\Arora\rtaa\layers"
    project = r"G:\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"
    p = ArcProPrint(webmap.read(), layer_dir, project)
    p.print_page("Test-Page-Title")
