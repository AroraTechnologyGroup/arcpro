import arcpy
from arcpy import mp

project = r"G:\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"
gdb = r"G:\GIS Data\Arora\rtaa\MasterGDB_05_25_16\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"


class LayerRepairTool:
    def __init__(self, project_path):
        self.aprx = mp.ArcGISProject(project_path)
        self.m = self.aprx.listMaps('Map')[0]
        self.lyrs = self.m.listLayers()

    def repair(self, target_gdb):
        for l in self.lyrs:
            try:
                print("connectionProperties: {}".format(l.connectionProperties))
                conProp = l.connectionProperties
                conProp['connection_info']['database'] = target_gdb
                l.connectionProperties = conProp
            except TypeError:
                pass

        self.aprx.save()
        return self.aprx

if __name__ == "__main__":
    rp = LayerRepairTool(project_path=project)
    rp.repair(target_gdb=gdb)
