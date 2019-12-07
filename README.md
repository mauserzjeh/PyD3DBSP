# PyD3DBSP
Blender add-on for importing Call of Duty 2 map files

Current status:
  - Tested with Blender 2.79b
  - Basic import of map geometry from .d3dbsp files
  - UVs
  - Materials & textures
  - Entities (xmodels)
  
TODO:
  - Fix overlapping faces
      - Need to remove duplicate faces and create blended materials based on vertex color, so decals will display correctly
  - Custom Normals
  - Optimalization for better speed
  - Additional error handling and refactoring
