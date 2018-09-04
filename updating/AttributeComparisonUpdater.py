import arcpy
from arcpy import mp
from arcpy import da

# web_fc = arcpy.GetParameterAsText(0)
web_fc = r"C:\ESRI_WORK_FOLDER\rtaa\spaces\Space_8_29_18\c222b57d726042bbabfc0d4a2242d5ef.gdb\Space"

# target_fc = arcpy.GetParameterAsText(1)
target_fc = r"E:\DatabaseConnections\RTAA\RTAA_Master_Replica.sde\RTAA_MasterGDB.DBO.Interior\RTAA_MasterGDB.DBO.Space"


def get_root_name(fc):
    """return the final portion of the feature class name"""
    base_name = arcpy.Describe(fc).baseName
    x = base_name.split(".")[-1]
    return x


# the rule is that the input fc name must match the target fc name
if get_root_name(web_fc) != get_root_name(target_fc):
    message = "source fc name does not match the target fc name"
    arcpy.AddError(message)
    raise Exception(message)

web_guids = []
target_guids = []

with da.SearchCursor(web_fc, ["src_GlobalID"]) as cursor:
    for row in cursor:
        web_guids.append(row[0])


with da.SearchCursor(target_fc, ["GLOBALID"]) as cursor:
    for row in cursor:
        target_guids.append(row[0])


new_web_guids = [x for x in web_guids if x not in target_guids]
if len(new_web_guids):
    arcpy.AddError("These src_GlobalID values don't exist in the target fc: {}".format(new_web_guids))
    raise Exception()
missing_web_guids = [x for x in target_guids if x not in web_guids]
if len(missing_web_guids):
    arcpy.AddError("These GLOBALID values were not found in the web fc: {}".format(missing_web_guids))
    raise Exception()


# find the common fields between the two fcs and update if values have been modified
# editor tracking and other system fields will not match from FGDB to SDE

drop_fields = ["SRC_GLOBALID", "SHAPE", "GLOBALID", "LAST_EDITED_DATE", "LAST_EDITED_USER", "CREATED_DATE", "CREATED_USER", "OBJECTID"]

web_fields = [x.name for x in arcpy.ListFields(web_fc) if x.name.upper() not in drop_fields]
target_fields = [x.name for x in arcpy.ListFields(target_fc) if x.name.upper() not in drop_fields]

web_fields.sort()
target_fields.sort()

if web_fields != target_fields:
    arcpy.AddError("These fields were found in the web fc but not in the target fc: {}".format([x for x in web_fields if x not in target_fields]))
    arcpy.AddError("These fields were found in the target fc but not in the web fc: {}".format(
        [x for x in target_fields if x not in web_fields]))

common_fields = [x for x in web_fields if x in target_fields]

arcpy.AddMessage("These are the common fields being compared between the feature classes :: {}".format(common_fields))
# iterating through all of the target features and updating their attributes from the web fc

update_cnt = 0
with da.UpdateCursor(target_fc, ["GlobalID"].extend(common_fields)) as cursor:
    for row in cursor:
        guid = row[0]
        atts = row[1:]

        needs_update = False
        new_row = row
        searcher = da.SearchCursor(web_fc, common_fields, "src_GlobalID = '{}'".format(guid))
        for _row in searcher:
            for i in range(len(_row)):
                if _row[i] != atts[i]:
                    needs_update = True
                    break
            if needs_update:
                new_row = _row
        # check if the new_row has been updated, if so update target_row
        if new_row != row:
            cursor.updateRow(new_row)
            update_cnt += 1

arcpy.AddMessage("{} rows were updated".format(update_cnt))

