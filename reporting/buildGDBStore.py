import arcpy
from arcpy import env
import json
import os
import xlwt


class DescribeGDB:
    def __init__(self, workspace):
        self.workspace = workspace
        self.desc = arcpy.Describe(workspace)
        pass

    def describe(self):
        env.workspace = self.workspace
        _desc = self.desc
        context = dict()
        context["baseName"] = _desc.baseName
        context["workspaceType"] = _desc.workspaceType
        context["catalogPath"] = _desc.catalogPath
        context["workspaceFactoryProgID"] = _desc.workspaceFactoryProgID
        context["release"] = _desc.release
        context["domains"] = _desc.domains
        context["currentRelease"] = _desc.currentRelease
        context["connectionString"] = _desc.connectionString
        datasets = arcpy.ListDatasets()
        context["datasets"] = []
        try:
            if len(datasets):
                for dataset in datasets:
                    props = dict()
                    env.workspace = "{}\\{}".format(self.workspace, dataset)
                    descdata = arcpy.Describe(env.workspace)
                    props["baseName"] = descdata.baseName
                    props["changeTracked"] = descdata.changeTracked
                    props["datasetType"] = descdata.datasetType
                    props["isVersioned"] = descdata.isVersioned
                    props["children"] = ", ".join([d.name for d in descdata.children])

                    props["spatialReference.XYResolution"] = descdata.spatialReference.XYResolution
                    props["spatialReference.ZResolution"] = descdata.spatialReference.ZResolution
                    props["spatialReference.domain"] = descdata.spatialReference.domain
                    props["spatialReference.factoryCode"] = descdata.spatialReference.factoryCode
                    props["spatialReference.name"] = descdata.spatialReference.name
                    props["spatialReference.PCSName"] = descdata.spatialReference.PCSName
                    props["spatialReference.PCSCode"] = descdata.spatialReference.PCSCode
                    props["spatialReference.GCSCode"] = descdata.spatialReference.GCSCode
                    props["spatialReference.GCSName"] = descdata.spatialReference.GCSName

                    fclist = arcpy.ListFeatureClasses()
                    props["feature_classes"] = []

                    if len(fclist) > 0:
                        fclist.sort()
                        for fc in fclist:
                            count = 0
                            with arcpy.da.SearchCursor(fc, "*") as cursor:
                                for row in cursor:
                                    count += 1

                            if count:
                                sub_props = dict()
                                descfc = arcpy.Describe(fc)
                                sub_props["catalogPath"] = descfc.catalogPath
                                sub_props["baseName"] = descfc.baseName
                                sub_props["count"] = count
                                sub_props["featureType"] = descfc.featureType
                                sub_props["hasM"] = descfc.hasM
                                sub_props["hasZ"] = descfc.hasZ
                                sub_props["hasSpatialIndex"] = descfc.hasSpatialIndex
                                sub_props["shapeFieldName"] = descfc.shapeFieldName
                                sub_props["shapeType"] = descfc.shapeType
                                props["feature_classes"].append(sub_props)

                    if len(props["feature_classes"]):
                        context["datasets"].append(props)

        except Exception as e:
            print("{}".format(e))

        return json.dumps(context, sort_keys=True, separators=(',', ':'), indent=4)

if __name__ == "__main__":
    x = DescribeGDB(r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB_05_25_16\RTAA_Delivery_05_25_16.gdb")
    desc = x.describe()
    print(desc)
