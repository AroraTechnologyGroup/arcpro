import arcpy
from arcpy import mp

project_path = r"G:\Documents\ArcGIS\Projects\RTAA_Printing\RTAA_Printing.aprx"
target_gdb = r"G:\GIS Data\Arora\rtaa\MasterGDB_05_25_16\MasterGDB_05_25_16\MasterGDB_05_25_16.gdb"
aprx = mp.ArcGISProject(project_path)
m = aprx.listMaps('Map')[0]
lyrs = m.listLayers()
for l in lyrs:
    try:
        print("connectionProperties: {}".format(l.connectionProperties))

        conProp = l.connectionProperties
        conProp['connection_info']['database'] = target_gdb
        l.connectionProperties = conProp
    except TypeError:
        pass


aprx.save()
