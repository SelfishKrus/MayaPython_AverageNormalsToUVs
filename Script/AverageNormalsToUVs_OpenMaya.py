import maya.cmds as cmds
import maya.api.OpenMaya as om
import numpy as np

import os

# Functions
def DebugPrint(header, message, index, num=5):
    if index < num:
        print(f"{index}: {header}: {message}")

# Octahedron compression

def OctWrap(v):
    return (1.0 - np.abs(v[::-1])) * (np.where(v >= 0.0, 1.0, -1.0))

def Encode(n):
    n = np.array([n.x, n.y, n.z])
    n /= (np.abs(n[0]) + np.abs(n[1]) + np.abs(n[2]))
    
    if n[2] >= 0.0:
        n[:2] = n[:2]
    else:
        n[:2] = OctWrap(n[:2])
    
    n[:2] = n[:2] * 0.5 + 0.5
    return n[:2]

def Decode(f):
    f = f * 2.0 - 1.0
    n = np.array([f[0], f[1], 1.0 - np.abs(f[0]) - np.abs(f[1])])
    t = np.clip(-n[2], 0, 1)  # saturate in HLSL clamps between 0 and 1
    n[:2] += np.where(n[:2] >= 0.0, -t, t)
    return n / np.linalg.norm(n)  # normalize

def main():
    # Get distance threshold
    result = cmds.promptDialog(
                    title = "Average Normals",
                    message = "Distance threshold",
                    text="0.1",
                    button = ["OK", "Cancel"],
                    defaultButton = "OK",
                    cancelButton = "Cancel",
                    dismissString = "Cancel")

    if result == "OK":
        str_distance = cmds.promptDialog(query=True, text=True)
        float_distance = float(str_distance)
        
        # a list contains full DAG
        selectModels = cmds.ls(sl=True)
        selectList = om.MGlobal.getActiveSelectionList()
        
        if len(selectModels) == 0:
            cmds.error("Please select at least one object.")
            return
        
        # Main logic
        else:
            # each object
            for index, model in enumerate(selectModels):
                
                print("#############################################")
                print(f"{model}: Start")
                print("------------------------------------")

                ############ Prepare ############
                dagPath = selectList.getDagPath(index)
                fnMesh = om.MFnMesh(dagPath)
                itMeshPolygon = om.MItMeshPolygon(dagPath)

                uvIndexToWriteIn = 2
                uvSetNames = []
                uvSetNames = fnMesh.getUVSetNames()

                encodedNormals = [] * fnMesh.numFaceVertices

                ############ Check out UV Set ############
                if len(uvSetNames) < 3:
                    print(f"ERROR: only {len(uvSetNames)} uv sets, please add to 3 uv sets.")
                    return
                
                if itMeshPolygon.hasUVs(uvSetNames[uvIndexToWriteIn]):
                    print(f"{uvSetNames[uvIndexToWriteIn]} is valid")
                else:
                    print(f"ERROR: {uvSetNames[uvIndexToWriteIn]} is invalid")
                    return
                
                print("Check out UV Set Order")
                for i, uvSetName in enumerate(uvSetNames):
                    print(f"UV[{i}] : {uvSetName}")
                print(f"Write into UVSET[{uvIndexToWriteIn}] : {uvSetNames[uvIndexToWriteIn]}")
                print("------------------------------------")

                ############ Store original normals ############
                originalNormals = om.MVectorArray()    
                originalNormals = fnMesh.getNormals()
                print("Store orignal normals - Finished")
                print("------------------------------------")

                ############ Get TBN Matrix ############
                matrice_OStoTS = om.MMatrixArray()
                matrice_OStoTS.setLength(fnMesh.numFaceVertices)

                faceVertexCount = 0

                itMeshPolygon.reset()
                while (not itMeshPolygon.isDone()):
                    globalFaceId = itMeshPolygon.index()
                    for i in range(itMeshPolygon.polygonVertexCount()):
                        globalVertexId = itMeshPolygon.vertexIndex(i)
                        normalOS = om.MVector()
                        tangetnOS = om.MVector()
                        binormalOS = om.MVector()
                        normalOS = fnMesh.getFaceVertexNormal(globalFaceId, globalVertexId, space=om.MSpace.kObject)
                        tangentOS = fnMesh.getFaceVertexTangent(globalFaceId, globalVertexId, space=om.MSpace.kObject)
                        binormalOS = fnMesh.getFaceVertexBinormal(globalFaceId, globalVertexId, space=om.MSpace.kObject)
                        matrix_TStoOS = om.MMatrix([tangentOS.x,    tangentOS.y,    tangentOS.z,    0.0,
                                                    binormalOS.x,   binormalOS.y,   binormalOS.z,   0.0,
                                                    normalOS.x,     normalOS.y,     normalOS.z,     0.0,
                                                    0.0,            0.0,            0.0,            1.0])
                        matrix_OStoTS = matrix_TStoOS.transpose()
                        matrice_OStoTS[faceVertexCount] = matrix_OStoTS

                        faceVertexCount += 1
                    
                    itMeshPolygon.next()

                # --- test --- 
                print(f"len(matrice_OStoTS): {len(matrice_OStoTS)}")

                ############ Average normals ############
                cmds.select(model)
                cmds.polyAverageNormal(distance=float_distance)
                print("Average normals - Finished")
                print("------------------------------------")

                ############ Encode and store ############
                setUVLoopCount = 0
                matrixId = 0
                itMeshPolygon.reset()
                while (not itMeshPolygon.isDone()):
                    
                    # get average normal
                    globalFaceId = itMeshPolygon.index()
                    # each vertex in face
                    for i in range(itMeshPolygon.polygonVertexCount()):
                        globalVertexId = itMeshPolygon.vertexIndex(i)
                        avgNormalOS = om.MVector()
                        avgNormalOS = fnMesh.getFaceVertexNormal(globalFaceId, globalVertexId, space=om.MSpace.kObject)
                        avgNormalTS = om.MVector()
                        avgNormalTS = avgNormalOS * matrice_OStoTS[matrixId]
                        DebugPrint("avgNormalTS", avgNormalTS, setUVLoopCount)
                    
                        # octahedron compression
                        avgNormalTS_encoded = Encode(avgNormalTS)
                        DebugPrint("avgNormalOS_encoded", avgNormalTS_encoded, setUVLoopCount)

                        # Set uv
                        itMeshPolygon.setUV(i, avgNormalTS_encoded, uvSet=uvSetNames[uvIndexToWriteIn])
                        
                        DebugPrint("*", "*", setUVLoopCount)
                        matrixId += 1
                        setUVLoopCount += 1

                    itMeshPolygon.next()

                print(f"Set UV Loop Count: {setUVLoopCount}")
                print("Average normals to UV - Finished")
                print("------------------------------------")

                ########### Set original normals ############
                fnMesh.setNormals(originalNormals)
                print(f"len(originalNormals): {len(originalNormals)}")
                print("Set original normals - Finished")
                print("------------------------------------")

                print(f"{model}: Done")
                print("#############################################")

            outputPath = r'G:\GithubProjects\MayaPython_AverageNormalsToUVs\ProjectTest'
            outputName = r'TestCube.fbx'
            outputPath = os.path.join(outputPath, outputName)

            cmds.select(selectModels)
            cmds.file(outputPath, force=True, options="v=0;embedTextures=0;", typ="FBX export", pr=True, es=True)

            print(f"{model}: Exported to {outputPath}")
            print("#############################################")

            cmds.delete(selectModels)
            cmds.file(outputPath, i=True, options="v=0;mo=0;ImportMaterials=DoNotImportMaterials;")

            print(f"{model}: Imported from {outputPath}")
            print("#############################################")

if __name__ == "__main__":
    main()