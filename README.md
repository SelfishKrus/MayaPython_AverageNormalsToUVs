# MayaPython_AverageNormalsToUVs

a maya python plugin to write average normals of a mesh into uvs, by maya.api.OpenMaya library

## Prerequisites

- Enable **dx11shader.mll** in Maya plugin manager for shader preview

## Procedure

- For each object in the selection list
    - Store original vertex normals for recovery
    - Average vertex normals
    - Fetch averaged vertex normal at face-vertex level and encode it into UV2 with octahedron compression
    - Decode average normals in vertex shader

## Tips

- Otherwise [AverageNormalsToUVs.py] may not.
- Create a new dx11shader material and link it to /Shader/DXS_NormalDisplay.
- Check out Surface Data bound with corresponding semantics in dx11ShaderMaterial
- Before executing [AverageNormalsToUVs.py], please check out these steps:
    - Make sure there are 3 UV sets in the model, and UV values are not NULL.
    - Check out UV index order with [PrintUVSets.py](http://printuvsets.py/) cuz  it’s not always in order as UV Editor presents.

## Demo

![Untitled](Average%20Normals%20To%20UVs%2073986e57b33e449a9bf4214d3664b39c/Untitled.png)

## Ref

[Maya工作流的平滑法线描边小工具](https://zhuanlan.zhihu.com/p/538660626)

[[Maya API] Vertex tangent space](https://discourse.techart.online/t/maya-api-vertex-tangent-space/4079/2)

[Octahedron normal vector encoding](https://knarkowicz.wordpress.com/2014/04/16/octahedron-normal-vector-encoding/)

