import bpy
import copy


# Parameters
num_x = 5 # Number of cubes in the x-direction
num_y = 5 # Number of cubes in the y-direction
num_z = 5  # Number of cubes in the z-direction
cube_size = 4.0  # Size of each cube


horizontal_layer = []
cubes = []

counter_column = 0
column_list = []
all_columns = []


class Grid():
    def __init__(self,num_x,num_y,num_z):
        self.grid_num_columns = num_x*num_y
        self.grid_num_yz_surface = num_x
        self.all_columns = self.construct_all_columns_scheme()
        self.surfaces_yz = self.construct_yz_surface_scheme()
        
    def construct_all_columns_scheme(self):
        all_columns = {}
        for i in range(0,self.grid_num_columns):
            all_columns['column'+str(i)] = []
        return all_columns
    
    def construct_yz_surface_scheme(self):
        yz_surfaces = {}
        for i in range(0,self.grid_num_yz_surface):
            yz_surfaces['surface_yz'+str(i)] = []
        return yz_surfaces
    
    def select_column(self,column_index):
        column_name = 'column'+str(column_index)
        for each_column in self.all_columns:
            if each_column == column_name:
                for cube in self.all_columns[column_name]:
                    cube.select_set(True)
                    
                return self.all_columns[column_name]
            
        print(column_name+' '+'could not be found')
        
    
    def select_surface_yz(self,surface_yz_index):
        surface_yz_name = 'surface_yz'+str(surface_yz_index)
        for each_surface in self.surfaces_yz:
            if each_surface == surface_yz_name:
                for cube in self.surfaces_yz[surface_yz_name]:
                    cube.select_set(True)
                return self.surfaces_yz[surface_yz_name]
    

def create_grid(num_x,num_y,num_z,cube_size=1):
    # Parameters
    #num_x = 5  # Number of cubes in the x-direction
    #num_y = 3  # Number of cubes in the y-direction
    #num_z = 4  # Number of cubes in the z-direction
    #cube_size = 1.0  # Size of each cube
    
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    

    # Create cubes in a grid
    grid = Grid(num_x,num_y,num_z)
    column_counter = 0
    yz_surface_counter = -1
    for i in range(num_x):
        building_surface_yz = True
        yz_surface_counter = yz_surface_counter + 1
        for j in range(num_y):
            for k in range(num_z):
                bpy.ops.mesh.primitive_cube_add(size=cube_size, enter_editmode=False, location=(i * cube_size, j * cube_size, k * cube_size))
                cube = bpy.context.active_object
                cubes.append(cube)
                if len(grid.all_columns['column'+str(column_counter)]) == num_z:
                    column_counter = column_counter+1
                grid.all_columns['column'+str(column_counter)].append(cube)
                grid.surfaces_yz['surface_yz'+str(yz_surface_counter)].append(cube)
    # Update the scene
    bpy.context.view_layer.update()
    return grid
    
grid = create_grid(num_x,num_y,num_z,cube_size=cube_size)
surface = grid.select_surface_yz(2)
print(surface)

