import arcpy
from arcpy import env
from arcpy import da
import time
import os
from collections import Counter

env.overwriteOutput = 1
path = os.path.abspath(os.path.dirname(__file__))


class DescribeGDB:
    def __init__(self, workspace):
        self.workspace = workspace
        desc = arcpy.Describe(workspace)
        self.basename = desc.basename
        pass

    def describe(self):
        context = dict()
        domains = arcpy.da.ListDomains(self.workspace)
        context["GDB_name"] = self.basename
        context["domains"] = domains
        env.workspace = self.workspace
        datasets = arcpy.ListDatasets()
        context["datasets"] = []
        try:
            if len(datasets):
                for dataset in datasets:
                    props = dict()
                    env.workspace = "{}\\{}".format(self.workspace, dataset)
                    descdata = arcpy.Describe(env.workspace)
                    props['description'] = descdata

                    # List feature classes inside dataset and add a field for each one
                    fclist = arcpy.ListFeatureClasses()
                    props['feature_classes'] = []

                    if len(fclist) > 0:
                        fclist.sort()
                        for fc in fclist:
                            sub_props = dict()
                            descfc = arcpy.Describe(fc)
                            sub_props['name'] = descfc.basename
                            sub_props['description'] = descfc
                            sub_props['fields'] = []
                            count = int(arcpy.GetCount_management(fc).getOutput(0))
                            sub_props['count'] = count
                            fields = arcpy.ListFields(fc)

                            keeplist = []
                            droplist = []
                            for field in fields:
                                values = dict()
                                if field.type.upper() not in ["BLOB", "GEOMETRY", "OID", "GUID"] and \
                                                field.name.upper() not in ["SHAPE_LENGTH", "SHAPE", "GUID",
                                                                           "CREATED_USER", "CREATED_DATE",
                                                                           "LAST_EDITED_USER", "LAST_EDITED_DATE"]:
                                    keeplist.append(field)
                                else:
                                    droplist.append(field)

                                print(field.name)
                                values['name'] = field.name
                                values['aliasName'] = field.aliasName
                                values['domain'] = field.domain
                                values['editable'] = field.editable
                                values['isNullable'] = field.isNullable
                                values['length'] = field.length
                                values['precision'] = field.precision
                                values['required'] = field.required
                                values['scale'] = field.scale
                                values['type'] = field.type

                                attributes = []
                                summary = []

                                if field in keeplist:
                                    fcount = int(arcpy.GetCount_management(fc).getOutput(0))

                                    if fcount > 0:
                                        with da.SearchCursor(fc, field.name) as cursor:
                                            for row in cursor:
                                                attributes.append(str(row[0]))

                                        c = Counter(attributes)
                                        counts = c.items()
                                        print(counts)

                                        i = 0
                                        for value in attributes:
                                            try:
                                                D = float(value)
                                                D = int(D)
                                            except:
                                                D = value

                                            if str(D) not in ['', ' ', '0', 'None', '<Null>']:
                                                i += 1

                                        percent = float(i)/fcount * 100.00
                                        percent = "%.2f" % percent

                                        print("i / fcount = {}".format(percent))
                                        if float(percent) < 75:
                                            droplist.append(field)
                                            keeplist.remove(field)
                                    else:
                                        summary.append("No attributes were found for field {}".format(field.name))
                                        droplist.append(field)
                                        keeplist.remove(field)
                                        percent = 0.0

                                elif field in droplist:
                                    percent = 0.0
                                if field in droplist and field not in keeplist:
                                    flag = "drop"
                                elif field in keeplist and field not in droplist:
                                    flag = "pass"
                                elif field in keeplist and field in droplist:
                                    flag = "error, in both lists"

                                values['percent'] = percent
                                values['flag'] = flag

                                if field.type.upper() not in ["BLOB", "GEOMETRY", "OID",
                                                              "GUID"] and field.name.upper() not in ["SHAPE_LENGTH",
                                                                                                     "SHAPE", "GUID",
                                                                                                     "CREATED_USER",
                                                                                                     "CREATED_DATE",
                                                                                                     "LAST_EDITED_USER",
                                                                                                     "LAST_EDITED_DATE"
                                                                                                     ]:
                                    sub_props['fields'].append(values)

                            props['feature_classes'].append(sub_props)

                    context['datasets'].append(props)
        except Exception as e:
            print("{}".format(e))

        return context

if __name__ == "__main__":
    x = DescribeGDB(r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB_05_25_16\RTAA_Delivery_05_25_16.gdb")
    desc = x.describe()
    print(desc)
