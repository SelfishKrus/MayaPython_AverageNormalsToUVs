import sys
print(sys.version)

import maya

import os
import tempfile
import FbxCommon

import maya.api.OpenMaya as om
import pymel

import pymel.core as pm
import pymel.core.nodetypes as nt
from maya import mel

import FbxCommon
from fbx import FbxDocumentInfo, FbxNodeAttribute, FbxVector4

import maya.standalone
import maya.cmds as cmds

import math

def AverageNormals(mesh):
    controlPoints = mesh.GetControlPoints()
    vertices = mesh.GetPolygonVertices()
    print(f'[DEBUG] len(controlPoints): {len(controlPoints)}')
    print(f'[DEBUG] len(vertices): {len(vertices)}')

    originalNormals = mesh.GetElementNormal()
    faceVertexNormals = mesh.CreateElementNormal()

    # Set to face normal 
    for polygonIndex in range(mesh.GetPolygonCount()):
        p1, p2, p3 = FbxVector4(), FbxVector4(), FbxVector4()
        p1 = controlPoints[mesh.GetPolygonVertex(polygonIndex, 0)]
        p2 = controlPoints[mesh.GetPolygonVertex(polygonIndex, 1)]
        p3 = controlPoints[mesh.GetPolygonVertex(polygonIndex, 2)]

        faceVertexNormal = FbxVector4()
        faceVertexNormal = (p1 - p3).CrossProduct(p2 - p1)

        for _ in range(mesh.GetPolygonSize(polygonIndex)):
            faceVertexNormals.GetDirectArray().Add(faceVertexNormal)

    # Average normals
    vertexData = {}
    for polygonIndex in range(mesh.GetPolygonCount()):
        for vertexIndex in range(mesh.GetPolygonSize(polygonIndex)):
            vertexId = mesh.GetPolygonVertex(polygonIndex, vertexIndex)
            lNormal = FbxVector4()
            lNormal = faceVertexNormals.GetDirectArray().GetAt(vertexId)
            
            if vertexId not in vertexData:
                vertexData[vertexId] = {'sumNormal': FbxVector4(0,0,0,0), "count": 0}
            
            vertexData[vertexId]['sumNormal'] += lNormal
            vertexData[vertexId]['count'] += 1

    for vertexId, data in vertexData.items():
        averageNormal = data['sumNormal'] / data['count']
        originalNormals.GetDirectArray().SetAt(vertexId, averageNormal)

    print(f'[DEBUG] len(faceVertexNormals): {faceVertexNormals.GetDirectArray().GetCount()}')
    print(f'[DEBUG] len(originalNormals): {originalNormals.GetDirectArray().GetCount()}')

def SetNormals(mesh, smoothNormals):
    meshElementNormals = mesh.GetElementNormal()
    meshElementNormals.Clear()
    for smoothNormal in smoothNormals.GetDirectArray():
        meshElementNormals.GetDirectArray().Add(smoothNormal)

    
def GetOriginalNormals(mesh):
    orginalElementNormals = mesh.GetElementNormal()
    print(f'[DEBUG] orginalElementNormals: {orginalElementNormals}')
    print(f'[DEBUG] orginalElementNormalsCount : {orginalElementNormals.GetDirectArray().GetCount()}')
    print(f'[DEBUG] originalElemantNormalAtIndex5 : {orginalElementNormals.GetDirectArray().GetAt(5)}')
    return orginalElementNormals

def GetTbnMatrix(mesh):
    print(f"[DEBUG] mesh : {mesh}")
    normals_element = mesh.GetElementNormal()
    tangeants_element = mesh.GetElementTangent()
    binormals_element = mesh.GetElementBinormal()

    normals_count = normals_element.GetDirectArray().GetCount()
    tangeants_count = tangeants_element.GetDirectArray().GetCount()
    binormals_count = binormals_element.GetDirectArray().GetCount()

    print(f'[DEBUG] normals_element: {normals_element}')
    print(f'[DEBUG] tangeants_element: {tangeants_element}')
    print(f'[DEBUG] binormals_element: {binormals_element}')

    print(f'[DEBUG] normals_count: {normals_count}')
    print(f'[DEBUG] tangeants_count: {tangeants_count}')
    print(f'[DEBUG] binormals_count: {binormals_count}')

    if normals_element and tangeants_element and binormals_element:
        for i in range(normals_element.GetDirectArray().GetCount()):
            normal = normals_element.GetDirectArray().GetAt(i)
    else:
        print(f'[ERROR] No normals/tangents/binormals found in {node.GetName()}')

# custom functions
def mainLogic(node):
    mesh = node.GetNodeAttribute()
    if mesh and mesh.GetAttributeType() == FbxNodeAttribute.EType.eMesh:
        # orginalElementNormals = GetOriginalNormals(mesh)
        AverageNormals(mesh)
        # SetNormals(mesh, smoothNormals)
        # GetTbnMatrix(mesh)
        FbxCommon.SaveScene(manager, scene, outputFbxPath, 0)

# ==========================   Main   ========================== # 

if __name__ == "__main__":
    # current path
    currentPath = os.getcwd()
    inputFbxPath = r"G:\GithubProjects\MayaPython_AverageNormalsToUVs\Script\FBXSample\GG_NAG_V5.fbx"
    outputFbxPath = r"G:\GithubProjects\MayaPython_AverageNormalsToUVs\Script\FBXSample\output.fbx"
    print(f'[DEBUG] inputFbxPath: {inputFbxPath}')
    print(f'[DEBUG] outputFbxPath: {outputFbxPath}')

    # Read fbx
    manager, scene = FbxCommon.InitializeSdkObjects()
    result = FbxCommon.LoadScene(manager, scene, inputFbxPath)
    assert result, u"无法打开 FBX 文件 %s" % inputFbxPath

    rootNode = scene.GetRootNode()
    print(f'[DEBUG] rootNode: {rootNode}')

    for i in range(rootNode.GetChildCount()):
        node = rootNode.GetChild(i)
        print(f'[DEBUG] node: {node}')
        mainLogic(node)
        print("######################################################################")