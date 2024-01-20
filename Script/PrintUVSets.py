import maya.cmds as cmds
import maya.api.OpenMaya as om
import numpy as np

selectModels = cmds.ls(sl=True, l=True)
selectList = om.MGlobal.getActiveSelectionList()

for index, model in enumerate(selectModels):
    dagPath = selectList.getDagPath(index)
    fnMesh = om.MFnMesh(dagPath)
    itMeshPolygon = om.MItMeshPolygon(dagPath)
    
    uvSetNames = []
    uvSetNames = fnMesh.getUVSetNames()
    
    for i, uvSetName in enumerate(uvSetNames):
        print(f"UV[{i}] : {uvSetName}")