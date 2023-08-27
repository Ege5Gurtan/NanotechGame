import bpy
import importlib.util


def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gm = include_module('grid_manager.py')
mm = include_module('material_manager.py')


grid = gm.create_grid(5,5,5)
selected_surface = grid.select_surface_xy(0)
test_material = mm.create_material('test',1,0,0,0)

#print(test_material)
for cube in selected_surface:
    print(cube)

#print(cube)
#for cube in selected_surface:
#    mm.assign_material(cube,test_material)
