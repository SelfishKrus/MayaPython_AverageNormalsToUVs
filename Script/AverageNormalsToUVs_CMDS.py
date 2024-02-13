import maya.cmds as cmds
import maya.api.OpenMaya as om
import numpy as np

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
                uvToWriteIn = uvSetNames[uvIndexToWriteIn]

                numVertices = fnMesh.numVertices

                ############ Check out UV Set ############
                if len(uvSetNames) < 3:
                    print(f"ERROR: only {len(uvSetNames)} uv sets, please add to 3 uv sets.")
                    return
                
                if itMeshPolygon.hasUVs(uvToWriteIn):
                    print(f"{uvToWriteIn} is valid")
                else:
                    print(f"ERROR: {uvToWriteIn} is invalid")
                    return
                
                print("Check out UV Set Order")
                for i, uvSetName in enumerate(uvSetNames):
                    print(f"UV[{i}] : {uvSetName}")
                print(f"Write into UVSET : {uvToWriteIn}")
                print("------------------------------------")

                ############ Store original normals ############
                originalNormals = om.MFloatVectorArray()    
                originalNormals = fnMesh.getNormals()
                print("Store orignal normals - Finished")
                print("------------------------------------")

                ############ Average normals ############
                cmds.select(model)
                cmds.polyAverageNormal(distance=float_distance)
                print("Average normals - Finished")
                print("------------------------------------")

                cmds.polyUVSet( currentUVSet=True,  uvSet=uvToWriteIn)

                ############ Encode to UV ######### ###
                # get avg vertex normal
                for i in range(numVertices):
                    cmds.select(clear=True)
                    cmds.select(f'{model}.vtx[{i}]')
                    avgNormals = cmds.polyNormalPerVertex(q=True, xyz=True)
                    avgNormal = np.array([0.0, 0.0, 0.0])
                    for j in range(len(avgNormals)//3):
                        avgNormal += avgNormals[j*3:j*3+3]
                    
                    mag = np.linalg.norm(avgNormal)
                    avgNormal /= mag
                    
                    # encode
                    avgNormal = om.MFloatVector(avgNormal[0], avgNormal[1], avgNormal[2])
                    avgNormal_encoded = Encode(avgNormal)

                    cmds.select(f'{model}.map[{i}]')
                    cmds.polyEditUV(u=avgNormal_encoded[0], v=avgNormal_encoded[1], r=False, uvs=uvToWriteIn)

                cmds.polyUVSet( currentUVSet=True,  uvSet=uvSetNames[0])
                
            
                
                print("Average normals to UV - Finished")
                print("------------------------------------")

                ########### Set original normals ############
                fnMesh.setNormals(originalNormals)
                print(f"len(originalNormals): {len(originalNormals)}")
                print("Set original normals - Finished")
                print("------------------------------------")

                print(f"{model}: Done")
                print("#############################################")

if __name__ == "__main__":
    main()