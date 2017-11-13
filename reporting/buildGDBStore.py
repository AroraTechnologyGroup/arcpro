import arcpy
from arcpy import env
import json
import os
from collections import Counter
import argparse
import sys


class DescribeGDB:
    """Gathers details about a geodatabase"""
    def __init__(self, workspace):
        self.workspace = workspace
        self.desc = arcpy.Describe(workspace)
        pass

    def describe(self):
        env.workspace = self.workspace
        _desc = self.desc
        context = dict()
        context["baseName"] = _desc.baseName
        context["catalogPath"] = _desc.catalogPath
        context["workspaceType"] = _desc.workspaceType
        context["workspaceFactoryProgID"] = _desc.workspaceFactoryProgID
        context["release"] = _desc.release
        context["domains"] = _desc.domains
        context["currentRelease"] = _desc.currentRelease
        context["connectionString"] = _desc.connectionString
        datasets = arcpy.ListDatasets()
        context["datasets"] = datasets

        return json.dumps(context, sort_keys=True, separators=(',', ':'), indent=4)


class DescribeFDataset:
    """Gathers details about a Feature Dataset"""
    def __init__(self, workspace, dataset):
        self.workspace = os.path.join(workspace, dataset)
        self.desc = arcpy.Describe(self.workspace)

    def describe(self):
        env.workspace = self.workspace
        descdata = self.desc
        props = dict()
        props["baseName"] = descdata.baseName
        props["changeTracked"] = descdata.changeTracked
        props["datasetType"] = descdata.datasetType
        props["isVersioned"] = descdata.isVersioned
        props["spatialReference"] = descdata.spatialReference.factoryCode
        props["XYResolution"] = descdata.spatialReference.XYResolution
        props["ZResolution"] = descdata.spatialReference.ZResolution
        props["PCSName"] = descdata.spatialReference.PCSName
        props["PCSCode"] = descdata.spatialReference.PCSCode
        props["GCSCode"] = descdata.spatialReference.GCSCode
        props["GCSName"] = descdata.spatialReference.GCSName

        fclist = arcpy.ListFeatureClasses()
        props["children"] = fclist

        return json.dumps(props, sort_keys=True, separators=(',', ':'), indent=4)


class DescribeFClass:
    """Gathers information about a Feature Class"""
    def __init__(self, workspace, dataset, fclass):
        self.workspace = os.path.join(workspace, dataset)
        self.fclass = fclass

    def describe(self):
        env.worksace = self.workspace
        fc = self.fclass

        count = 0
        with arcpy.da.SearchCursor(fc, "*") as cursor:
            for row in cursor:
                count += 1

        props = dict()
        descfc = arcpy.Describe(fc)
        props["catalogPath"] = descfc.catalogPath
        props["baseName"] = descfc.baseName
        props["count"] = count
        props["featureType"] = descfc.featureType
        props["hasM"] = descfc.hasM
        props["hasZ"] = descfc.hasZ
        props["hasSpatialIndex"] = descfc.hasSpatialIndex
        props["shapeFieldName"] = descfc.shapeFieldName
        props["shapeType"] = descfc.shapeType
        fields = [f.name for f in arcpy.ListFields(fc)]
        props["fields"] = fields

        return json.dumps(props, sort_keys=True, separators=(',', ':'), indent=4)


class DescribeField:

    def __init__(self, _workspace, _dataset, _fc, _field):
        self.workspace = os.path.join(_workspace, _dataset)
        self.fc = _fc
        self.field = _field

    def describe(self):
        env.workspace = self.workspace
        infc = self.fc
        in_field = self.field
        field = arcpy.ListFields(infc, "{}".format(in_field))[0]
        props = dict()

        props["name"] = field.name
        props["aliasName"] = field.aliasName
        props["baseName"] = field.baseName
        props["defaultValue"] = field.defaultValue
        props["domain"] = field.domain
        props["editable"] = field.editable
        props["isNullable"] = field.isNullable
        props["length"] = field.length
        props["precision"] = field.precision
        props["required"] = field.required
        props["scale"] = field.scale
        props["type"] = field.type
        system_field_types = ["BLOB", "GEOMETRY", "OID", "GLOBALID"]
        system_field_names = ["SHAPE_LENGTH", "SHAPE_AREA", "SHAPE", "OBJECTID", "GLOBALID"]
        editor_field_names = ["CREATED_USER", "CREATED_DATE", "LAST_EDITED_USER", "LAST_EDITED_DATE"]
        system_field_names.extend(editor_field_names)
        props["attributes"] = dict()
        props["percent"] = ""

        if field.type.upper() not in system_field_types and field.name not in system_field_names:
            attributes = []
            cnt = 0
            with arcpy.da.SearchCursor(infc, in_field) as cursor:
                for row in cursor:
                    if row[0] is None:
                        d = "None"
                    else:
                        try:
                            d = "{}".format(row[0])
                        except UnicodeEncodeError:
                            d = row[0].encode('ascii', 'ignore')
                    attributes.append(d)
                    cnt += 1
            if cnt:
                c = Counter(attributes)
                counts = c.items()
                for x in counts:
                    props["attributes"][x[0]] = x[1]

                del c

                i = 0
                for value in attributes:
                    try:
                        d = float(value)
                        d = int(d)
                    except ValueError:
                        d = value

                    if d not in ['', ' ', '0', 'None', '<Null>']:
                        i += 1
                    del d

                percent = float(i) / cnt * 100.00
                props["percent"] = "%.2f" % percent

            else:
                props["percent"] = '0.0'

        return json.dumps(props, sort_keys=True, separators=(',', ':'), indent=4)


if __name__ == "__main__":
    """
    1. If the gdb is provided and no other parameters, then the entire model will be built
    2. If the dataset is provided, then only that dataset will be analyzed
    3. If the feature class is provided, then only that feature class will be analyzed
    4. If the field is provided, the only that field will be analyzed
    
    * the gdb must be provided
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-gdb', help='this is the path to the geodatabase')
    parser.add_argument('-dataset', help='this is the dataset to analyze')
    parser.add_argument('-featureclass', help='this is a single feature class to analyze')
    parser.add_argument('-field', help='this is a single field to analyze')
    args = parser.parse_args()

    gdb = args.gdb
    if args.dataset is not None:
        dataset = args.dataset
    if args.featureclass is not None:
        featureClass = args.featureClass
    if args.field is not None:
        field = args.field

    x = DescribeGDB(gdb)

    gdb_output = x.describe()

    sys.stdout.buffer.write(gdb_output)

    if dataset:
        "We are only processing this one dataset"
        datasets = [dataset]
    else:
        datasets = json.loads(gdb_output)["datasets"]

    for dataset in datasets:
        desc_dataset = DescribeFDataset(gdb, dataset)
        dset_output = desc_dataset.describe()
        sys.stdout.buffer.write(dset_output)

        if featureClass:
            fclist = [featureClass]
        else:
            fclist = json.loads(dset_output)["children"]

        for fc in fclist:
            obj = DescribeFClass(gdb, dataset, fc)
            fc_out = obj.describe()
            sys.stdout.buffer.write(fc_out)

            if field:
                fields = [field]
            else:
                fields = [f.name for f in arcpy.ListFields(fc)]

            for field in fields:
                f_obj = DescribeField(gdb, dataset, fc, field)
                f_out = f_obj.describe()
                sys.stdout.buffer.write(f_out)

