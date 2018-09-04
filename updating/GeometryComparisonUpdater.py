import arcpy
from arcpy import mp

input_fc = arcpy.GetParameterAsText(0)
compare_fc = arcpy.GetParameterAsText(1)

try:
    p = mp.ArcGISProject("CURRENT")
    m = p.activeMap
except OSError:
    pass

new_oids = []

with arcpy.da.SearchCursor(input_fc, ["OID@", "SHAPE@"]) as cursor:
    for row in cursor:
        oid = row[0]
        geo = row[-1]
        matched = False
        searcher = arcpy.da.SearchCursor(compare_fc, "SHAPE@")
        for _row in searcher:
            if _row[0].equals(geo):
                matched = True
                break
        del searcher
        if not matched:
            new_oids.append(oid)

name = "NewFeatures"
if arcpy.Exists(name):
    arcpy.Delete_management(name)
temp_layer = arcpy.MakeFeatureLayer_management(input_fc, name, "OBJECTID IN ('{}')".format("', '".join(new_oids))).getOutput(0)
del new_oids
m.addLayer(temp_layer)

# now add the stale features from the compare fc that don't have a match in the input_fc, these feature geometries can be
# replaced using the Spatial Adjustment toolbar in ArcMap.

stale_oids = []

with arcpy.da.SearchCursor(compare_fc, ["OID@", "SHAPE@"]) as cursor:
    for row in cursor:
        oid = row[0]
        geo = row[-1]
        matched = False
        searcher = arcpy.da.SearchCursor(input_fc, "SHAPE@")
        for _row in searcher:
            if _row[0].equals(geo):
                matched = True
                break
        del searcher
        if not matched:
            stale_oids.append(oid)

name = "StaleFeatures"
if arcpy.Exists(name):
    arcpy.Delete_management(name)
temp_layer2 = arcpy.MakeFeatureLayer_management(compare_fc, name, "OBJECTID IN ('{}')".format("', '".join(stale_oids))).getOutput(0)
del stale_oids

m.addLayer(temp_layer2)
p.save()
