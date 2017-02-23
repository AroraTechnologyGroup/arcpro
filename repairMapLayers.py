import arcpy
from arcpy import mp
import argparse


class LayerRepairTool:
    def __init__(self, project):
        self.aprx = mp.ArcGISProject(project)

    def repair(self, target_gdb):
        m = self.aprx.listMaps('Map')[0]
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
        project = r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"

    if args.gdb is not None:
        gdb = args.gdb
    else:
        gdb = r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
    rp = LayerRepairTool(project_path=project)
    rp.repair(target_gdb=gdb)
