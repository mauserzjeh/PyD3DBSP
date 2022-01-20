### This tool is not supported anymore. A new version can be found here: https://github.com/mauserzjeh/cod-asset-importer

# PyD3DBSP
Blender add-on for importing Call of Duty 2 map files

[Check out how the tool works (alpha state)](https://www.youtube.com/watch?v=TIuK9BN_9kY)

Current status:
  - Tested with Blender 2.81
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
