import arcpy
from arcpy import da
from arcpy import mp

lease_status = arcpy.ListFields('Space_1', "LEASE_STATUS")[0]
status_domain = lease_status.domain

space_use = arcpy.ListFields('Space_1', "SPACE_USE")[0]
use_domain = space_use.domain

p = mp.ArcGISProject("CURRENT")
map = p.listMaps("LPM*")[0]
space_lyr = map.listLayers("Space_1")[0]
geodatabase = space_lyr.connectionProperties["connection_info"]["database"]
domains = da.ListDomains(geodatabase)

status_list = []
use_list = []

for domain in domains:
    if domain.name == status_domain:
        coded_values = domain.codedValues
        status_list.extend([v for k,v in iter(coded_values.items())])

    elif domain.name == use_domain:
        coded_values = domain.codedValues
        use_list.extend([v for k,v in iter(coded_values.items())])

total_list = []
for use in use_list:
    for status in status_list:
        total_list.append((use, status))

i =0
with da.UpdateCursor('Space_1', ["SPACE_USE", "LEASE_STATUS"]) as cursor:
    for row in cursor:
        if i < len(total_list):
            new_row = total_list[i]
            i += 1
            cursor.updateRow(new_row)
        else:
            new_row = (None, None)
            cursor.updateRow(new_row)
