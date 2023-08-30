import bpy
import copy


class Grid():
    def __init__(self,num_x,num_y,num_z,cube_size=1):
        self.num_x = num_x
        self.num_y = num_y
        self.num_z = num_z
        self.cube_size = cube_size
        self.grid_num_columns = num_x*num_y
        self.grid_num_yz_surface = num_x
        self.grid_num_xy_surface = num_z
        self.grid_num_xz_surface = num_y
        self.all_columns = self.construct_all_columns_scheme()
        self.surfaces_yz = self.construct_yz_surface_scheme()
        self.surfaces_xy = self.construct_xy_surface_scheme()
        self.surfaces_xz = self.construct_xz_surface_scheme()
        self.cubes = []
        self.cube_indices = {}
        
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
        if not(cube_index == None):
            self.cubes[cube_index].select_set(True)
            return self.cubes[cube_index]
        else:
            return None
    
    
    def select_grid_corners(self):
        num_x = self.num_x
        num_y = self.num_y
        num_z = self.num_z
        
        grid_corners = []
        grid_corners.append(self.select_cube(0))
        grid_corners.append(self.select_cube(num_z-1))
        grid_corners.append(self.select_cube(num_z*(num_y-1)))
        grid_corners.append(self.select_cube(num_z*(num_y)-1))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-1))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-num_z))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-(num_y*num_z)))
        grid_corners.append(self.select_cube(num_z*(num_y)*(num_x)-(num_y*num_z)+num_z-1))
        
        return grid_corners
        
    def get_cube_index(self,cube):
        pass        
        

class Grid_Cube:
    def __init__(self,grid,cube_index):
        self.grid = grid
        self.cube_size = grid.cube_size
        self.total_cube_number = grid.num_x*grid.num_y*grid.num_z
        self.cube_index = cube_index
        self.neighbour_z_cube_index = cube_index+1
        self.neighbour_minus_z_cube_index = cube_index-1
        self.neighbour_x_cube_index = cube_index + grid.num_z*grid.num_y 
        self.neighbour_minus_x_cube_index = cube_index - grid.num_z*grid.num_y
        self.neighbour_y_cube_index = cube_index + grid.num_z
        self.neighbour_minus_y_cube_index = cube_index - grid.num_z
        
        self.verify_neighbour_existance()
        
        self.neighbour_z_cube = grid.select_cube(self.neighbour_z_cube_index)
        self.neighbour_minus_z_cube = grid.select_cube(self.neighbour_minus_z_cube_index)
        
        self.neighbour_x_cube = grid.select_cube(self.neighbour_x_cube_index)
        self.neighbour_minus_x_cube = grid.select_cube(self.neighbour_minus_x_cube_index)
        
        self.neighbour_y_cube = grid.select_cube(self.neighbour_y_cube_index)
        self.neighbour_minus_y_cube = grid.select_cube(self.neighbour_minus_y_cube_index)
        
        bpy.ops.object.select_all(action='DESELECT')
        
    def verify_neighbour_existance(self):
        cube = self.grid.select_cube(self.cube_index)
        cube_center_point = self.get_cube_center_point(cube)
        
        neighbour_z_center = tuple(map(sum,zip(cube_center_point,(0,0,self.cube_size))))
        neighbour_minus_z_center = tuple(map(sum,zip(cube_center_point,(0,0,-self.cube_size))))
        
        neighbour_y_center = tuple(map(sum,zip(cube_center_point,(0,self.cube_size,0))))
        neighbour_minus_y_center = tuple(map(sum,zip(cube_center_point,(0,-self.cube_size,0))))
        
        neighbour_x_center = tuple(map(sum,zip(cube_center_point,(self.cube_size,0,0))))
        neighbour_minus_x_center = tuple(map(sum,zip(cube_center_point,(-self.cube_size,0,0))))
        
        neighbour_z_existance = self.is_point_inside_grid(neighbour_z_center,self.grid)
        neighbour_minus_z_existance = self.is_point_inside_grid(neighbour_minus_z_center,self.grid)
        
        neighbour_y_existance = self.is_point_inside_grid(neighbour_y_center,self.grid)
        neighbour_minus_y_existance = self.is_point_inside_grid(neighbour_minus_y_center,self.grid)
        
        neighbour_x_existance = self.is_point_inside_grid(neighbour_x_center,self.grid)
        neighbour_minus_x_existance = self.is_point_inside_grid(neighbour_minus_x_center,self.grid)
        
        if not(neighbour_z_existance):
            self.neighbour_z_cube_index = None
        if not(neighbour_minus_z_existance):
            self.neighbour_minus_z_cube_index = None
        if not(neighbour_y_existance):
            self.neighbour_y_cube_index = None
        if not(neighbour_minus_y_existance):
            self.neighbour_minus_y_cube_index = None
        if not(neighbour_x_existance):
            self.neighbour_x_cube_index = None
        if not(neighbour_minus_x_existance):
            self.neighbour_minus_x_cube_index = None
    
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
    
    
    @staticmethod
    def get_cube_center_point(test_cube):
        test_center_v = test_cube.matrix_world @ test_cube.location
        test_point = (test_center_v.x,test_center_v.y,test_center_v.z)
        return test_point
    
    @staticmethod
    def is_cube_inside_grid(test_cube,grid):
        test_point = self.get_cube_center_point(test_cube)
        is_inside = self.is_point_inside_grid(test_point,grid)
        return is_inside
        
    @staticmethod
    def is_point_inside_grid(test_point,grid):
        edge_cubes = grid.select_grid_corners()
        corner_points = []
        for obj in edge_cubes:
            center_coordinates = obj.matrix_world @ obj.location
            corner_points.append((center_coordinates.x,center_coordinates.y,center_coordinates.z))
        
        min_x, min_y, min_z = map(min, zip(*corner_points))
        max_x, max_y, max_z = map(max, zip(*corner_points))
        x, y, z = test_point

        if min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z:
            return True
        else:
            return False
    
    @staticmethod
    def print_neighbour_indices(cube):
        print('+z : ' + str(cube.neighbour_z_cube_index))
        print('-z : ' + str(cube.neighbour_minus_z_cube_index))
        print('+x : ' + str(cube.neighbour_x_cube_index))
        print('-x : ' + str(cube.neighbour_minus_x_cube_index))
        print('+y : ' + str(cube.neighbour_y_cube_index))
        print('-y : ' + str(cube.neighbour_minus_y_cube_index))
    
        
        

        
        
     
    
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
    grid = Grid(num_x,num_y,num_z,cube_size=cube_size)
    column_counter = 0
    cube_counter = 0
    yz_surface_counter = -1
    for i in range(num_x):
        yz_surface_counter = yz_surface_counter + 1
        for j in range(num_y):
            for k in range(num_z):
                bpy.ops.mesh.primitive_cube_add(size=cube_size, enter_editmode=False, location=(i * cube_size, j * cube_size, k * cube_size))
                cube = bpy.context.active_object
                grid.cubes.append(cube)
                grid.cube_indices[cube] = cube_counter
                cube_counter = cube_counter +1
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
#num_x = 4 # Number of cubes in the x-direction
#num_y = 5 # Number of cubes in the y-direction
#num_z = 6  # Number of cubes in the z-direction
#cube_size = 8.0  # Size of each cube
#grid = create_grid(num_x,num_y,num_z,cube_size=cube_size)
##cube = Grid_Cube(grid,32)
#selected_cubes = cube.select_cube(z=True,_z=True,x=True,_x=True,y=True,_y=True,itself=False)
#print(selected_cubes)
#cube = grid.select_cube(2)
#print(grid.cube_indices[cube])


