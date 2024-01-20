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

- Create a new dx11shader material and link it to /Shader/DXS_NormalDisplay.
- Check out Surface Data bound with corresponding semantics in dx11ShaderMaterial
- Before executing [AverageNormalsToUVs.py],
    - Make sure there are 3 UV sets in the model, and UV values are not NULL.
    - Check out UV index order with [PrintUVSets.py] cuz it’s not always in order as UV Editor presents.

## Demo

![Comparison](https://github.com/SelfishKrus/MayaPython_AverageNormalsToUVs/assets/79186991/e595c16b-1218-43ea-a82e-06046cc2cab2)

## Ref

[Maya工作流的平滑法线描边小工具](https://zhuanlan.zhihu.com/p/538660626)

[Octahedron normal vector encoding](https://knarkowicz.wordpress.com/2014/04/16/octahedron-normal-vector-encoding/)

[[Maya API] Vertex tangent space](https://discourse.techart.online/t/maya-api-vertex-tangent-space/4079/2)
