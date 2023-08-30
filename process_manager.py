import bpy
import importlib.util


def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gm = include_module('grid_manager.py')
mm = include_module('material_manager.py')

def check_if_cube_has_material(cube):
    if hasattr(cube,"data") and hasattr(cube.data,"materials") and (len(cube.data.materials) > 0):
        return True
    else:
        return False

def Deposit(thickness,grid,material):
    for column_index in range(0,grid.grid_num_columns):
        column = grid.select_column(column_index)
        number_of_deposited_cubes = 0
        for cube in column:
            cube_index = grid.cube_indices[cube]
            grid_cube = gm.Grid_Cube(grid,cube_index)
            
            if number_of_deposited_cubes < thickness:
                
                deposit = False
                
                #check if minus z neighbour of the cube has material assigned
                bottom_has_material = check_if_cube_has_material(grid_cube.neighbour_minus_z_cube)
                
                #check if the cube has already a material assigned
                itself_has_material = check_if_cube_has_material(cube)
                
                if bottom_has_material and not(itself_has_material):
                    deposit = True
                elif grid_cube.neighbour_minus_z_cube == None and not(itself_has_material):
                    deposit = True
                
                if deposit:
                    mm.assign_material(cube,material)
                    number_of_deposited_cubes +=1


grid = gm.create_grid(6,7,8,cube_size=10)
test_material = mm.create_material('test',1,0,0,0)
test_material2 = mm.create_material('test2',1,1,0,0)
Deposit(3,grid,test_material)
Deposit(2,grid,test_material2)
