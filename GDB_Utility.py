import arcpy
from arcpy import env
import os


class GDBReferenceObject:

    def __init__(self, path):
        self.path = path

    def build_dict(self):
        """Create a feature class lookup dict to speed up runtime"""
        ingdb = self.path
        env.workspace = ingdb
        datasets = arcpy.ListDatasets()
        output = dict()
        for d in datasets:
            fcs = arcpy.ListFeatureClasses("", "", d)
            output[d] = fcs
        return output


if __name__ == "__main__":
    GDBRef = GDBReferenceObject(path=r"D:\EsriGDB\ConnectionFiles\Sub-Default_MasterGDB.sde")
    out = GDBRef.build_dict()
    print(out)
