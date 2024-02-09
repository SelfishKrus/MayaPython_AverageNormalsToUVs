import sys
sys.path.append(r'')
print(sys.path)

import os
import tempfile

# import maya

# import pymel.core as pm
# import pymel.core.nodetypes as nt
from maya import mel

import FbxCommon
from fbx import FbxDocumentInfo,FbxNodeAttribute

# current path
currentPath = os.path.dirname(os.path.abspath(__file__))
outputFbxPath = os.path.join(currentPath, 'output.fbx')
print(f'outputFbxPath: {outputFbxPath}')