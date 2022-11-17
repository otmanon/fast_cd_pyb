import sys
sys.path.append('C:\\Users\\otmanbench\\Desktop\\utils\\BlenderToolbox\\') # change this to your path to “path/to/BlenderToolbox/
import BlenderToolBox as bt
import os, bpy, bmesh
import numpy as np

cwd = os.getcwd()

name = "raptor"
## initialize blender
imgRes_x = 800 
imgRes_y = 800 
numSamples = 200
exposure = 1.5 
## read mesh from numpy arrayss
location = (0,-0.25,-0.25)
rotation = (90, 0,0) 
scale = (0.25, 0.25,0.25)


result_dir = "./results/fit_modes/stingray/";
try: 
  os.mkdir(result_dir) 
except OSError as error: 
  print(error)   

V = np.load( result_dir + "V.npy") # np.array([[1,1,1],[-1,1,-1],[-1,-1,1],[1,-1,-1]], dtype=np.float32) # vertex list

F=np.load(result_dir + "F.npy")
P_up = np.load( result_dir + "P_up.npy") 
P_down = np.load( result_dir + "P_down.npy") 
P_lbs_down = np.load( result_dir + "P_down_lbs.npy") 
P_disp_down = np.load( result_dir + "P_down_disp.npy") 

P_lbs_up = np.load( result_dir + "P_up_lbs.npy") 
P_disp_up = np.load( result_dir + "P_up_disp.npy") 

for method in ["rest", "ref_down", "lbs_down", "disp_down", "ref_up", "lbs_up", "disp_up"]:
  print ("############## " + method)
  outputPath = os.path.join(cwd, result_dir + "/" + method +  '.png') 

  bt.blenderInit(imgRes_x, imgRes_y, numSamples, exposure)
  X = V;
  RGBA = (0.5, 0.5, 0.5, 1)

  if (method == "ref_down"):
    X = P_down
    RGBA = (173.0/255, 221.0/255, 142.0/255, 1)
  if (method == "lbs_down"):
    X = P_lbs_down
    RGBA = (144.0/255, 210.0/255, 236.0/255, 1)
  elif (method == "disp_down"):
    X = P_disp_down
    RGBA = (250/255, 114.0/255, 104.0/255, 1)
  if (method == "ref_up"):
    X = P_up
    RGBA = (173.0/255, 221.0/255, 142.0/255, 1)
  if (method == "lbs_up"):
    X = P_lbs_up
    RGBA = (144.0/255, 210.0/255, 236.0/255, 1)
  elif (method == "disp_up"):
    X = P_disp_up
    RGBA = (250/255, 114.0/255, 104.0/255, 1)
  mesh = bt.readNumpyMesh(X,F,location,rotation,scale)
  ob = bpy.data.objects.get('numpy mesh object')

    #set lighting to smooth. 
  for poly in ob.data.polygons:
    poly.use_smooth = True

  #set lighting to smooth. 
  #for poly in ob.data.polygons:
    #  poly.use_smooth = True


  # mesh = bt.setMeshScalars(mesh, vertex_scalars, color_map, color_type)
  
 
  meshColor = bt.colorObj(RGBA, 0.5, 1.0, 1.0, 0.0, 2.0)
  bt.setMat_plastic(mesh, meshColor)

  ## set camera (recommend to change mesh instead of camera, unless you want to adjust the Elevation)
  camLocation = (3, -3, -0.25)
  lookAtLocation = (0, 0, -0.25)#(-0.5,-0.3,0.5)
  focalLength = 45 # (UI: click camera > Object Data > Focal Length)
  cam = bt.setCamera(camLocation, lookAtLocation, focalLength)

  ## set light
  lightAngle = (6, 20, -45) 
  strength = 1
  shadowSoftness = 1
  sun = bt.setLight_sun(lightAngle, strength, shadowSoftness)

  ## set ambient light
  bt.setLight_ambient(color=(0.1,0.1,0.1,1)) 

  ## set gray shadow to completely white with a threshold 
  bt.shadowThreshold(alphaThreshold = 0.05, interpolationMode = 'CARDINAL')

  ## save blender file so that you can adjust parameters in the UI
  #bpy.ops.wm.save_mainfile(filepath=os.getcwd() + '/test.blend')

  # save rendering
  bt.renderImage(outputPath, cam)



