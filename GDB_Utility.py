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
            env.workspace = os.path.join(ingdb, d)
            fcs = arcpy.ListFeatureClasses()
            output[d] = fcs
        return output

