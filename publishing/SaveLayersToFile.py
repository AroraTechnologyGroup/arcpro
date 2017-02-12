import arcpy
from arcpy import mp
import os

out_folder = arcpy.GetParameterAsText(0)
# out_folder = r"C:\ESRI_WORK_FOLDER\rtaa\layers"
map = arcpy.GetParameterAsText(1)

# """For Testing"""
# p = mp.ArcGISProject(r"C:\Users\rhughes\Documents\ArcGIS\Projects\RTAA_publishing\RTAA_publishing.aprx")
# m = p.listMaps('LayerMap')[0]

p = mp.ArcGISProject('current')
p.save()
m = p.listMaps(map)[0]

layers = m.listLayers()
for l in layers:
    if l.isFeatureLayer:
        layer_name = l.name
        i = 0
        for dirpath, dirs, files in os.walk(out_folder):
            for file in files:
                name = file.replace(".lyrx", "")
                if layer_name == name:
                    save_path = os.path.join(dirpath, file)
                    if not i:
                        os.remove(save_path)
                        # arcpy.SaveToLayerFile_management(l, save_path)
                        l.saveACopy(save_path)
                        arcpy.AddMessage("Saved layer {} to file".format(name))
                        i += 1
                        break
                    else:
                        arcpy.AddWarning("Layer {} has already been saved, check for duplicate layers".format(name))
        if not i:
            arcpy.AddError("Unable to save layer file {}.  It must exist in the folder to be overwritten".format(layer_name))



