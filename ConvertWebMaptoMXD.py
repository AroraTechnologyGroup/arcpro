import arcpy
from arcpy import mapping
import json
import os
import sys

#Test values
# mapfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests/fixtures/webmap.json")
template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests/templates/RTAA.mxd")
# file = open(mapfile, 'r')
# webmap = file.read()


class MXDConvert:
    def __init__(self, json, layout, format):
        self.webmap = json
        self.layout = layout
        self.format = format
        pass

    def process_template(self):

        result = mapping.ConvertWebMapToMapDocument(self.webmap, template)
        mxd = result.mapDocument

        outfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output/WebMapMXD.pdf")
        mapping.ExportToPDF(mxd, outfile)
        out_bytes = open(outfile, 'rb')
        return out_bytes.read()

if __name__ == "__main__":
    webmap = sys.argv[1]
    layout = sys.argv[2]
    format = sys.argv[3]
    conv = MXDConvert(webmap, layout, format)
    print(conv.process_template())

