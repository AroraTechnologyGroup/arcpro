import arcpy
from arcpy import mp
import argparse
import os


class LayerRepairTool:
    def __init__(self, project_path):
        self.aprx = mp.ArcGISProject(project_path)

    def repair(self, target_gdb):
        m = self.aprx.listMaps('LocalMap')[0]
        lyrs = [x for x in m.listLayers() if x.isFeatureLayer]
        for l in lyrs:
            try:
                newProp = l.connectionProperties
                newProp['connection_info']['database'] = target_gdb
                l.updateConnectionProperties(l.connectionProperties, newProp)
            except TypeError:
                pass

        self.aprx.save()
        return self.aprx

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-project', help='the project with layers to repair')
    parser.add_argument('-gdb', help='the file path to the master gdb')

    args = parser.parse_args()

    if args.project is not None:
        project = args.project
    else:
        try:
            project = r"D:\ArcPro\RTAA_Printing_Publishing\RTAA_Printing_Publishing.aprx"
        except:
            project = arcpy.GetParameterAsText(0)

    if args.gdb is not None:
        gdb = args.gdb
    else:
        try:
            gdb = r"D:\EsriGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
        except:
            gdb = arcpy.GetParameterAsText(1)

    rp = LayerRepairTool(project_path=project)
    rp.repair(target_gdb=gdb)
