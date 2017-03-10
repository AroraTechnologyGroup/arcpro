import arcpy
from arcpy import mp
import argparse
import os


class LayerRepairTool:
    def __init__(self, project_path):
        self.aprx = mp.ArcGISProject(project_path)

    def repair(self, target_gdb):
        m = self.aprx.listMaps('LayerMap')[0]
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
        if not os.path.exists(project):
            project = r"C:\inetpub\rtaa_gis_data\RTAA_Printing\RTAA_Printing.aprx"

    if args.gdb is not None:
        gdb = args.gdb
    else:
        gdb = r"C:\ESRI_WORK_FOLDER\rtaa\MasterGDB\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
        if not os.path.exists(gdb):
            gdb = r"C:\inetpub\rtaa_gis_data\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"

    rp = LayerRepairTool(project_path=project)
    rp.repair(target_gdb=gdb)

