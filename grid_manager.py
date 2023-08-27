import bpy
import copy


class Grid():
    def __init__(self,num_x,num_y,num_z):
        self.num_x = num_x
        self.num_y = num_y
        self.num_z = num_z
        self.grid_num_columns = num_x*num_y
        self.grid_num_yz_surface = num_x
        self.grid_num_xy_surface = num_z
        self.grid_num_xz_surface = num_y
        self.all_columns = self.construct_all_columns_scheme()
        self.surfaces_yz = self.construct_yz_surface_scheme()
        self.surfaces_xy = self.construct_xy_surface_scheme()
        self.surfaces_xz = self.construct_xz_surface_scheme()
        self.cubes = []
        
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
    
    def construct_xy_surface_scheme(self):
        xy_surfaces = {}
        for i in range(0,self.grid_num_xy_surface):
            xy_surfaces['surface_xy'+str(i)] = []
        return xy_surfaces
    
    def construct_xz_surface_scheme(self):
        xz_surfaces = {}
        for i in range(0,self.grid_num_xz_surface):
            xz_surfaces['surface_xz'+str(i)] = []
        return xz_surfaces
    
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
            
    def select_surface_xy(self,surface_xy_index):
        surface_xy_name = 'surface_xy'+str(surface_xy_index)
        for each_surface in self.surfaces_xy:
            if each_surface == surface_xy_name:
                for cube in self.surfaces_xy[surface_xy_name]:
                    cube.select_set(True)
                return self.surfaces_xy[surface_xy_name]
            
    def select_surface_xz(self,surface_xz_index):
        surface_xz_name = 'surface_xz'+str(surface_xz_index)
        for each_surface in self.surfaces_xz:
            if each_surface == surface_xz_name:
                for cube in self.surfaces_xz[surface_xz_name]:
                    cube.select_set(True)
                return self.surfaces_xz[surface_xz_name]
    
    def select_cube(self,cube_index):
        self.cubes[cube_index].select_set(True)
        return self.cubes[cube_index]
    
    def select_grid_corners(self):
        self.select_cube(0)
        self.select_cube(num_z-1)
        self.select_cube(num_z*(num_y-1))
        self.select_cube(num_z*(num_y)-1)
        self.select_cube(num_z*(num_y)*(num_x)-1)
        self.select_cube(num_z*(num_y)*(num_x)-num_z)
        self.select_cube(num_z*(num_y)*(num_x)-(num_y*num_z))
        self.select_cube(num_z*(num_y)*(num_x)-(num_y*num_z)+num_z-1)
        
        
        

class Grid_Cube:
    def __init__(self,grid,cube_index):
        self.grid = grid
        self.total_cube_number = grid.num_x*grid.num_y*grid.num_z
        self.cube_index = cube_index
        
        
        self.neighbour_z_cube_index = cube_index+1
        self.neighbour_minus_z_cube_index = cube_index-1
        self.neighbour_x_cube_index = cube_index + grid.num_z*grid.num_y 
        self.neighbour_minus_x_cube_index = cube_index - grid.num_z*grid.num_y
        self.neighbour_y_cube_index = cube_index + grid.num_z
        self.neighbour_minus_y_cube_index = cube_index - grid.num_z
    
    def verify_neighbour_exist():
        pass
        #checks if neighbour of the Grid_Cube is within the grid boundaries
    
    def select_cube(self,itself=True,
    z=False,_z=False,
    y=False,_y=False,
    x=False,_x=False):
        selected_cubes = {'itself':None,'z':None,'_z':None,'y':None,'_y':None,'x':None,'_x':None}
        if itself:
            selected_cubes['itself']=self.grid.select_cube(self.cube_index)
        if z and not(self.neighbour_z_cube_index==None):
            selected_cubes['z']=self.grid.select_cube(self.neighbour_z_cube_index)
        if _z and not(self.neighbour_minus_z_cube_index==None):
            selected_cubes['_z']=self.grid.select_cube(self.neighbour_minus_z_cube_index)
        if y and not(self.neighbour_y_cube_index==None):
            selected_cubes['y']=self.grid.select_cube(self.neighbour_y_cube_index)
        if _y and not(self.neighbour_minus_y_cube_index==None):
            selected_cubes['_y']=self.grid.select_cube(self.neighbour_minus_y_cube_index)
        if x and not(self.neighbour_x_cube_index==None):
            selected_cubes['x']=self.grid.select_cube(self.neighbour_x_cube_index)
        if _x and not(self.neighbour_minus_x_cube_index==None):
            selected_cubes['_x']=self.grid.select_cube(self.neighbour_minus_x_cube_index)    
        return selected_cubes
        
    
    
                
     
    
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
        yz_surface_counter = yz_surface_counter + 1
        for j in range(num_y):
            for k in range(num_z):
                bpy.ops.mesh.primitive_cube_add(size=cube_size, enter_editmode=False, location=(i * cube_size, j * cube_size, k * cube_size))
                cube = bpy.context.active_object
                grid.cubes.append(cube)
                if len(grid.all_columns['column'+str(column_counter)]) == num_z:
                    column_counter = column_counter+1
                xz_surface_index = column_counter % num_y
                xy_surface_index = len(grid.all_columns['column'+str(column_counter)])
                grid.surfaces_xy['surface_xy'+str(xy_surface_index)].append(cube)
                grid.surfaces_xz['surface_xz'+str(xz_surface_index)].append(cube)
                grid.all_columns['column'+str(column_counter)].append(cube)
                grid.surfaces_yz['surface_yz'+str(yz_surface_counter)].append(cube)
                
    # Update the scene
    bpy.context.view_layer.update()
    return grid



# Parameters
num_x = 5 # Number of cubes in the x-direction
num_y = 5 # Number of cubes in the y-direction
num_z = 5  # Number of cubes in the z-direction
cube_size = 8.0  # Size of each cube
grid = create_grid(num_x,num_y,num_z,cube_size=cube_size)
grid.select_grid_corners()


#grid_cube = Grid_Cube(grid,5*6)
#selected_cubes = grid_cube.select_cube(_x=True,x=True,z=True)
#print(selected_cubes)

