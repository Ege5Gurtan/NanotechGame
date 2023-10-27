import bpy
import importlib.util
import os
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as patches
matplotlib.use('WebAgg')
from matplotlib.backend_bases import PickEvent
import threading
import multiprocessing
import psutil
import time
import keyboard
from functools import partial
import numpy as np


def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gm = include_module('grid_manager.py')
mm = include_module('material_manager.py')
um = include_module('ui_manager.py')
ifm = include_module('input_file_manager.py')


class Deposition():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material =  material
        self.resist_type = None
        self.order = order
        self.name = 'Deposition'
    
class Exposure():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Exposure'

class Development():
    def __init__(self,cubes,order):
        self.cubes = cubes
        self.order = order
        self.name = 'Development'
        
class Etching():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Etch'


class Polishing():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Polish'
        
class Doping():
    def __init__(self,cubes,material,order):
        self.cubes = cubes
        self.material = material
        self.order = order
        self.name = 'Dope'

class Diffusion():
    def __init__(self,cubes,diffusion_material,diffusion_medium_material,order):
        self.cubes = cubes
        self.diffusion_material = diffusion_material
        self.diffusion_medium_material = diffusion_medium_material
        self.order = order
        self.name = 'Diffuse'

class SpinCoating():
    def __init__(self,cubes,resist_material,resist_type,order):
        self.cubes = cubes
        self.resist_material = resist_material
        self.order = order
        self.name = 'SpinCoat'
        self.resist_type = resist_type


def Grid_SpinCoat(grid,material_name,resist_type,resist_thickness=1):
    surface_height_map = grid.get_top_surface_heights().values()
    surface_height_min_level = min(surface_height_map)
    surface_height_max_level = max(surface_height_map)
    deposition_amount = surface_height_max_level - surface_height_min_level
    spin_coated_resist_cubes = Grid_Deposit(deposition_amount,grid,material_name)
    Grid_Polish(material_name,grid)
    spin_coated_resist_cubes = spin_coated_resist_cubes + Grid_Deposit(resist_thickness,grid,material_name)
    
    
    return spin_coated_resist_cubes
    
def Grid_Deposit(thickness,grid,material_name):
    deposited_cubes = []
    for column_index in range(0,grid.grid_num_columns):
        column = grid.grid_select_column(column_index)
        number_of_deposited_cubes = 0
        for grid_cube in column:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            if number_of_deposited_cubes < thickness:
                deposit = False
                cube_index = grid.grid_cube_indices[grid_cube]
                bottom_neighbour_index = cube_index-1
                
                if grid_cube in grid.grid_surfaces_xy['surface_xy0']:
                    bottom_neighbour_index = None
                
                bottom_neighbour_grid_cube = grid.grid_select_cube(bottom_neighbour_index)
                
                bottom_grid_cube_has_material = mm.check_if_grid_cube_has_material(bottom_neighbour_grid_cube)
                grid_cube_itself_has_material = mm.check_if_grid_cube_has_material(grid_cube)
                
                if bottom_grid_cube_has_material and not(grid_cube_itself_has_material):
                    deposit = True
                elif bottom_neighbour_grid_cube == None and not(grid_cube_itself_has_material):
                    deposit = True
                
                if deposit:
                    grid_cube.material = material_name
                    number_of_deposited_cubes +=1
                    deposited_cubes.append(grid_cube)
                    grid.grid_cube_history[grid_cube][-1] = material_name

    return deposited_cubes
    


def Deposit(thickness,grid,material):
    deposited_cubes = []
    for column_index in range(0,grid.grid_num_columns):
        column = grid.select_column(column_index)
        number_of_deposited_cubes = 0
        for cube in column:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
            if number_of_deposited_cubes < thickness:
                deposit = False
                cube_index = grid.cube_indices[cube]
                bottom_neighbour_index = cube_index-1
                
                if cube in grid.surfaces_xy['surface_xy0']:
                    bottom_neighbour_index = None
                
                bottom_neighbour_cube = grid.select_cube(bottom_neighbour_index)
                bottom_has_material = mm.check_if_cube_has_material(bottom_neighbour_cube)
                #check if the cube has already a material assigned
                itself_has_material = mm.check_if_cube_has_material(cube)
                
                if bottom_has_material and not(itself_has_material):
                    deposit = True
                elif bottom_neighbour_cube == None and not(itself_has_material):
                    deposit = True
                
                if deposit:
                    mm.assign_material(cube,material,grid,add_to_history=False)
                    number_of_deposited_cubes +=1
                    deposited_cubes.append(cube)
                    grid.cube_history[cube][-1] = material
            #else:
            #    break
                    
    return deposited_cubes

clicked_tiles = []
def on_tile_click(event,scatter=[],ax=[],fig=[],all_patches=[]):
    print('you clicked')
    if event.artist in all_patches:
        #print('event artist index')
        ind = all_patches.index(event.artist)
        #print('ind')
    else:
        ind = event.ind
    label = event.artist.get_label()
    colors = scatter.get_facecolor()
    colors[ind[0]] = [1,0,0,1]
    scatter.set_facecolor(colors)
    #print(scatter.get_facecolor())
    ax.patches[ind[0]].set_facecolor('green')
    fig.canvas.draw()
    clicked_tiles.append(ind)

def Grid_Expose_Pattern_v2(grid,material_to_expose,pattern_df):
    exposed_indices = []
    counter = 0
    grid_size_z = grid.num_z
    for column in pattern_df:
        for index, value in enumerate(pattern_df[column]):
            if not(value == None):
                exposed_indices.append(counter)
            counter = counter +1

    
    exposed_cubes = []
    top_resist_layer_cubes = []
    
    top_surface_cubes_dict = grid.get_top_surface_cubes_with_material()
    top_surface_cubes_to_expose = []
    for column_name in top_surface_cubes_dict:
        cube = top_surface_cubes_dict[column_name]
        if cube.material == material_to_expose:
            top_surface_cubes_to_expose.append(cube)
    
    top_surface_cubes_dict_reversed = {v: k for k, v in top_surface_cubes_dict.items()}
    
    
    exposed_column_names = []
    if len(top_surface_cubes_to_expose) > 0:
    
        for i in exposed_indices:    
            exposed_cube = top_surface_cubes_to_expose[i]
            exposed_cube.material = material_to_expose+'_exposed'
            exposed_cube.is_exposed = True
            exposed_cubes.append(exposed_cube)
            column_name = top_surface_cubes_dict_reversed[exposed_cube]
            exposed_column_names.append(column_name)
        
        for exposed_column_name in exposed_column_names:
            for cube in grid.grid_all_columns[exposed_column_name]:
                if cube.material == material_to_expose:
                    cube.material = material_to_expose+'_exposed'
                    cube.is_exposed = True
                    if not(cube in exposed_cubes):
                        exposed_cubes.append(cube)
        
        #import pdb;pdb.set_trace();
                    
            
        for grid_cube in grid.grid_cubes:
            
            if grid_cube in exposed_cubes:
                grid.grid_cube_history[grid_cube].append(grid_cube.material)
            else:
                grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
  
    return exposed_cubes
 

def Expose_Pattern_v2(resist_layer_cubes,grid,material_to_expose,pattern_df):
    exposed_indices = []
    counter = 0
    for column in pattern_df:
        for index, value in enumerate(pattern_df[column]):
            if not(isinstance(value,float) and (np.isnan(value))):
                if not(value=='end'):
                    exposed_indices.append(counter)
            counter = counter +1


    exposed_cubes = []
    for i in exposed_indices:
        exposed_cube = resist_layer_cubes[i]
        exposed_cubes.append(exposed_cube)
        mm.assign_material(exposed_cube,material_to_expose,grid,add_to_history=False)
        
    for cube in grid.cubes:
        
        if cube in exposed_cubes:
            grid.cube_history[cube].append(material_to_expose)
        else:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
    #import pdb;pdb.set_trace();    
    return exposed_cubes
    
    
    

def Expose_Pattern(resist_layer_cubes,grid,material_to_expose):
    exposed_cubes = []
    number_of_pattern_tiles = grid.num_x*grid.num_y
    x_points = []
    y_points = []
    for i in resist_layer_cubes:
        point = gm.Grid_Cube.get_cube_center_point(i)
        x_points.append(point[0])
        y_points.append(point[1])
    
    plt.close('all')
    colors = []
    for i in range(0,number_of_pattern_tiles):
        colors.append('red')
    fig, ax = plt.subplots(nrows=1,ncols=1)
    scatter = ax.scatter(x_points, y_points, c=colors, picker=True,s=1000)
    sq_size = 20
    all_patches = []
    for xi,yi in zip(x_points,y_points):
        square = patches.Rectangle((xi-sq_size/2,yi-sq_size/2),sq_size,sq_size,fill=True,edgecolor='red')
        ax.add_patch(square)
        all_patches.append(square)
    
    click_event_function_wrapper=partial(on_tile_click,scatter=scatter,ax=ax,fig=fig,all_patches=all_patches)
    fig.canvas.mpl_connect('pick_event',click_event_function_wrapper)
    print('opening the browser')
    #threading.Event().set()
    ####EXPOSE
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Interactive Scatter Plot')
    #kill_open_browser()

    #thread = threading.Thread(target=plot_is_shown)
    #thread.start()
    plt.show()
    print('browser has been closed')
    
    
    for tile in clicked_tiles:
        ##ADD CONDITION - IF UP NEIGHBOR IS EMPTY, THE CUBE CAN BE EXPOSED
        tile_index = tile[0]
        exposed_cube = resist_layer_cubes[tile_index]
        mm.assign_material(exposed_cube,material_to_expose,grid,add_to_history=False)
        #grid.cube_history[exposed_cube].append(material_to_expose)
        exposed_cubes.append(exposed_cube)

    for cube in grid.cubes:
        if cube in exposed_cubes:
            grid.cube_history[cube].append(material_to_expose)
        else:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
            

    return exposed_cubes

def Grid_Develop_Pattern(resist_layer_cubes,material_name_to_develop,grid,resist_type='positive'):
    developed_cubes = []
    print('Resist type is: '+resist_type)
    for grid_cube in resist_layer_cubes:
        if resist_type == 'positive':
            if not(grid_cube.material == None) and (material_name_to_develop+'_exposed' == grid.grid_cube_history[grid_cube][-1]):
                grid_cube.material = None
                grid_cube.is_exposed = False
                developed_cubes.append(grid_cube)
                
           
        elif resist_type== 'negative':
            if not(grid_cube.material == None) and material_name_to_develop==grid_cube.material:
                grid_cube.material = None
                developed_cubes.append(grid_cube)
              
        else:
            print('Please specify resist_type as positive or negative')
            
    for grid_cube in grid.grid_cubes:
        if grid_cube in developed_cubes:
            grid.grid_cube_history[grid_cube].append('empty')
        else:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            

    return developed_cubes
            
def Develop_Pattern(resist_layer_cubes,material_name_to_develop,grid,resist_type='positive'):
    developed_cubes = []
    print('Resist type is: '+resist_type)
    for cube in resist_layer_cubes:
        
        if resist_type == 'positive':
            #import pdb;pdb.set_trace(); 
            
            if hasattr(grid.cube_history[cube][-1],"name") and material_name_to_develop in grid.cube_history[cube][-1].name:
                cube.data.materials.clear()### add empty material instead
                developed_cubes.append(cube)
                
        elif resist_type== 'negative':
            #import pdb;pdb.set_trace();
            if hasattr(grid.cube_history[cube][-1],"name") and not(material_name_to_develop in grid.cube_history[cube][-1].name):
                cube.data.materials.clear()
                developed_cubes.append(cube)
                
        else:
            print('Please specify resist_type as positive or negative')
            
    for cube in grid.cubes:
        if cube in developed_cubes:
            grid.cube_history[cube].append('empty')
        else:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
            
    return developed_cubes

def Remove_Cube_Material_Content(cubes,grid):
    removed_cubes = []
    for cube in cubes:
        cube.data.materials.clear()### add empty material instead
        removed_cubes.append(cube)
        grid.cube_history[cube].append('empty')
    cubes = gm.get_layer_difference(cubes,removed_cubes)
    return removed_cubes
        

def Grid_Etch(materials_to_etch,grid,etch_depth=100000000000):
    etched_cubes = []
    grid_size_z = grid.num_z
    #materials_to_etch = ['nitride','SIO2']
    #Etch(materials_to_etch,grid)
    for column in grid.grid_all_columns:
        column_cubes = grid.grid_all_columns[column]
        etched_cube_amount = 0
        for grid_cube in column_cubes[::-1]:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            cube_index = grid.grid_cube_indices[grid_cube]

            ##if cube itself has material to be etched and it above neighbour is empty            
            neighbour_z_cube_index = cube_index+1
            
            if grid_cube in grid.grid_surfaces_xy['surface_xy'+str(grid_size_z-1)]:
                neighbour_z_cube_index = None

            neighbour_z_cube = grid.grid_select_cube(neighbour_z_cube_index)
            
            top_has_material = mm.check_if_grid_cube_has_material(neighbour_z_cube)
            cube_has_material =  mm.check_if_grid_cube_has_material(grid_cube)
            name = grid_cube.material
            if not(name==None) and '_exposed' in name:
                #import pdb;pdb.set_trace();
                name = name.replace('_exposed',"")
                #import pdb;pdb.set_trace();

            if not(top_has_material) and cube_has_material and etched_cube_amount<etch_depth:
                for material_name in materials_to_etch:
                    if material_name in name: #or (material_name in name+'_exposed'):
                        grid_cube.material = None
                        grid_cube.is_exposed = False
                        etched_cubes.append(grid_cube)
                        grid.grid_cube_history[grid_cube][-1] = 'empty'
                        etched_cube_amount = etched_cube_amount + 1

    return etched_cubes

def Grid_Polish(material_to_polish,grid):
    polished_cubes = []
    for xy_surface in reversed(grid.grid_surfaces_xy):
        surface_cubes = grid.grid_surfaces_xy[xy_surface]
        found_materials = []
        for grid_cube in surface_cubes:
            material =  grid_cube.material
            found_materials.append(material)
        
        
        found_materials_without_none = [item for item in found_materials if item is not None]
        layer_to_remove = all(material_to_polish in item for item in found_materials_without_none)
        #import pdb;pdb.set_trace();
        if layer_to_remove:
            for grid_cube in surface_cubes:
                grid_cube.material = None
                polished_cubes.append(grid_cube)
        else:
            break
        
    for column in grid.grid_all_columns:
        column_cubes = grid.grid_all_columns[column]
        for grid_cube in column_cubes:
            if grid_cube in polished_cubes:
                grid.grid_cube_history[grid_cube].append('empty')
            else:
                #import pdb;pdb.set_trace();
                grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
    
    return polished_cubes


def Etch(materials_to_etch,grid,etch_depth=100000000000):
    etched_cubes = []
    grid_size_z = grid.num_z
    #materials_to_etch = ['nitride','SIO2']
    #Etch(materials_to_etch,grid)
    for column in grid.all_columns:
        column_cubes = grid.all_columns[column]
        etched_cube_amount = 0
        for cube in column_cubes[::-1]:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
            cube_index = grid.cube_indices[cube]

            ##if cube itself has material to be etched and it above neighbour is empty            
            neighbour_z_cube_index = cube_index+1
            if cube in grid.surfaces_xy['surface_xy'+str(grid_size_z-1)]:
                neighbour_z_cube_index = None
            neighbour_z_cube = grid.select_cube(neighbour_z_cube_index)
            
            #if not(neighbour_z_cube==None):
            top_has_material = mm.check_if_cube_has_material(neighbour_z_cube)
            cube_has_material =  mm.check_if_cube_has_material(cube)
            name = mm.get_material_name(cube)
            if not(top_has_material) and cube_has_material and etched_cube_amount<etch_depth:
                for material_name in materials_to_etch:
                    if material_name in name:                            
                        cube.data.materials.clear()
                        etched_cubes.append(cube)
                        grid.cube_history[cube][-1] = 'empty'
                        etched_cube_amount = etched_cube_amount + 1

                            
    
    return etched_cubes
                            


def Polish(material_to_polish,grid):
    polished_cubes = []
    for xy_surface in reversed(grid.surfaces_xy):
        surface_cubes = grid.surfaces_xy[xy_surface]
        found_materials = []
        for cube in surface_cubes:
            material =  mm.get_material_name(cube)
            found_materials.append(material)
        
        
        found_materials_without_none = [item for item in found_materials if item is not None]
        layer_to_remove = all(material_to_polish in item for item in found_materials_without_none)
        #import pdb;pdb.set_trace();
        if layer_to_remove:
            for cube in surface_cubes:
                cube.data.materials.clear()
                polished_cubes.append(cube)
    
    for column in grid.all_columns:
        column_cubes = grid.all_columns[column]
        for cube in column_cubes:
            if cube in polished_cubes:
                grid.cube_history[cube].append('empty')
            else:
                #import pdb;pdb.set_trace();
                grid.cube_history[cube].append(grid.cube_history[cube][-1])
    
    return polished_cubes

def Grid_Dope(doping_material,materials_to_dope,grid,doping_depth=2):
    doped_cubes = []
    grid_size_z = grid.num_z
    #materials_to_etch = ['nitride','SIO2']
    #Etch(materials_to_etch,grid)
    for column in grid.grid_all_columns:
        column_cubes = grid.grid_all_columns[column]
        doped_cube_amount = 0
        for grid_cube in column_cubes[::-1]:
            grid.grid_cube_history[grid_cube].append(grid.grid_cube_history[grid_cube][-1])
            cube_index = grid.grid_cube_indices[grid_cube]

            ##if cube itself has material to be etched and it above neighbour is empty            
            neighbour_z_cube_index = cube_index+1
            if grid_cube in grid.grid_surfaces_xy['surface_xy'+str(grid_size_z-1)]:
                neighbour_z_cube_index = None
            neighbour_z_cube = grid.grid_select_cube(neighbour_z_cube_index)
            
            top_has_material = mm.check_if_grid_cube_has_material(neighbour_z_cube)
            cube_has_material =  mm.check_if_grid_cube_has_material(grid_cube)
            if top_has_material:
                neighbour_z_cube_material_name = neighbour_z_cube.material
                if neighbour_z_cube_material_name == doping_material:
                    top_has_material = False
                    
            name = grid_cube.material
            if not(top_has_material) and cube_has_material and doped_cube_amount<doping_depth:
                for material_name in materials_to_dope:
                    if material_name in name:                         
                        grid_cube.material = doping_material
                        doped_cubes.append(grid_cube)
                        grid.grid_cube_history[grid_cube][-1] = doping_material
                        doped_cube_amount = doped_cube_amount + 1
    
    return doped_cubes
   
def Grid_Diffuse_xy(diffusion_material,diffusion_medium_material,grid,diffusion_radius):
    diffused_cubes = []
    for grid_cube in grid.grid_cubes:
        if grid_cube.material == diffusion_material:
            diffused_cube_index_pairs = gm.circular_grid_selector(grid.num_x,grid.num_y, grid_cube.index_x+1,grid_cube.index_y+1,diffusion_radius)
            xy_plane_grid_cubes = grid.grid_surfaces_xy['surface_xy'+str(grid_cube.index_z)]
            for cube_to_diffuse in xy_plane_grid_cubes:
                for index_pair in diffused_cube_index_pairs:
                    if cube_to_diffuse.index_x == index_pair[0]-1 and cube_to_diffuse.index_y == index_pair[1]-1:
                        if cube_to_diffuse.material == diffusion_medium_material:
                            if cube_to_diffuse not in diffused_cubes:
                                diffused_cubes.append(cube_to_diffuse)
    for diffused_cube in diffused_cubes:
        diffused_cube.material = diffusion_material
        grid.grid_cube_history[diffused_cube][-1] = diffusion_material
                                
    return diffused_cubes
    
def Grid_Diffuse_x(diffusion_material,diffusion_medium_material,grid,diffusion_amount):
    diffused_cubes = []
    for grid_cube in grid.grid_cubes:
        if grid_cube.material == diffusion_material:
            cube_index = grid.grid_cube_indices[grid_cube]
            for i in range(0,int(diffusion_amount)+1):
                neighbour_x_cube_index = cube_index + grid.num_z*grid.num_y*i
                neighbour_minus_x_cube_index = cube_index - grid.num_z*grid.num_y*i
                neighbour_x_cube = grid.grid_select_cube(neighbour_x_cube_index)
                neighbour_minus_x_cube = grid.grid_select_cube(neighbour_minus_x_cube_index)
                if neighbour_x_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_x_cube)
                if neighbour_minus_x_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_minus_x_cube)
    
    for diffused_cube in diffused_cubes:
        diffused_cube.material = diffusion_material
        grid.grid_cube_history[diffused_cube][-1] = diffusion_material
    
    return diffused_cubes
                

def Grid_Diffuse_y(diffusion_material,diffusion_medium_material,grid,diffusion_amount):
    diffused_cubes = []
    for grid_cube in grid.grid_cubes:
        if grid_cube.material == diffusion_material:
            cube_index = grid.grid_cube_indices[grid_cube]
            for i in range(0,int(diffusion_amount)+1):
                neighbour_y_cube_index = cube_index + grid.num_z*i
                neighbour_minus_y_cube_index = cube_index - grid.num_z*i
                neighbour_y_cube = grid.grid_select_cube(neighbour_y_cube_index)
                neighbour_minus_y_cube = grid.grid_select_cube(neighbour_minus_y_cube_index)
                if neighbour_y_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_y_cube)
                if neighbour_minus_y_cube.material == diffusion_medium_material:
                    diffused_cubes.append(neighbour_minus_y_cube)
    
    for diffused_cube in diffused_cubes:
        diffused_cube.material = diffusion_material
        grid.grid_cube_history[diffused_cube][-1] = diffusion_material
    
    return diffused_cubes
                
    

def Dope(doping_material,materials_to_dope,grid,doping_depth=1):
    doped_cubes = []
    grid_size_z = grid.num_z
    #materials_to_etch = ['nitride','SIO2']
    #Etch(materials_to_etch,grid)
    for column in grid.all_columns:
        column_cubes = grid.all_columns[column]
        doped_cube_amount = 0
        for cube in column_cubes[::-1]:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
            cube_index = grid.cube_indices[cube]

            ##if cube itself has material to be etched and it above neighbour is empty            
            neighbour_z_cube_index = cube_index+1
            if cube in grid.surfaces_xy['surface_xy'+str(grid_size_z-1)]:
                neighbour_z_cube_index = None
            neighbour_z_cube = grid.select_cube(neighbour_z_cube_index)
            
            top_has_material = mm.check_if_cube_has_material(neighbour_z_cube)
            cube_has_material =  mm.check_if_cube_has_material(cube)
            if top_has_material:
                neighbour_z_cube_material_name = mm.get_material_name(neighbour_z_cube)
                if neighbour_z_cube_material_name == doping_material.name:
                    top_has_material = False
                    
                
            name = mm.get_material_name(cube)
            if not(top_has_material) and cube_has_material and doped_cube_amount<doping_depth:
                
                for material_name in materials_to_dope:
                    if material_name in name:                            
                        mm.assign_material(cube,doping_material,grid,add_to_history=False)
                        doped_cubes.append(cube)
                        #grid.cube_history[cube].append(material_to_expose)
                        grid.cube_history[cube][-1] = doping_material.name
                        doped_cube_amount = doped_cube_amount + 1
    
    return doped_cubes



def Diffuse(diffusive_material,diffusion_medium_material,diffusivity_x,diffusivity_y,grid):
    
    cubes_with_diffusive_material = []
    neighbours_to_change = []
    for xy_surface in reversed(grid.surfaces_xy):
        surface_cubes = grid.surfaces_xy[xy_surface]
        
        for cube in surface_cubes:
            material =  mm.get_material_name(cube)
            if diffusive_material.name==material:
                cubes_with_diffusive_material.append(cube)
                cube_index = grid.cube_indices[cube]
                
                for next_neighbour_counter in range(1,diffusivity_x+1):
                    neighbour_x_cube_index = cube_index + grid.num_z*grid.num_y*next_neighbour_counter
                    neighbour_minus_x_cube_index = cube_index - grid.num_z*grid.num_y*next_neighbour_counter
                    if neighbour_x_cube_index<len(grid.cubes) and neighbour_x_cube_index>0:
                        neighbour_cube_x = grid.select_cube(neighbour_x_cube_index)
                        if neighbour_cube_x in surface_cubes:
                            neighbours_to_change.append(neighbour_cube_x)
                    
                    if neighbour_minus_x_cube_index<len(grid.cubes) and neighbour_minus_x_cube_index>0:
                        neighbour_cube_minus_x = grid.select_cube(neighbour_minus_x_cube_index)
                        if neighbour_cube_minus_x in surface_cubes:
                            neighbours_to_change.append(neighbour_cube_minus_x)
                            
                for next_neighbour_counter in range(1,diffusivity_y+1):
                    neighbour_y_cube_index = cube_index + grid.num_z*next_neighbour_counter
                    neighbour_minus_y_cube_index = cube_index - grid.num_z*next_neighbour_counter
                    
                    if neighbour_y_cube_index<len(grid.cubes) and neighbour_y_cube_index>0:
                        neighbour_cube_y = grid.select_cube(neighbour_y_cube_index)
                        if neighbour_cube_y in surface_cubes:
                            neighbours_to_change.append(neighbour_cube_y)
                    
                    if neighbour_y_cube_index<len(grid.cubes) and neighbour_y_cube_index>0:
                        neighbour_cube_minus_y = grid.select_cube(neighbour_minus_y_cube_index)
                        if neighbour_cube_minus_y in surface_cubes:
                            neighbours_to_change.append(neighbour_cube_minus_y)
                
                
                
    for neighbour_cube in neighbours_to_change:
        neighbour_cube_material_name = mm.get_material_name(neighbour_cube)
        if neighbour_cube_material_name == diffusion_medium_material.name:
            mm.assign_material(neighbour_cube,diffusive_material,grid,add_to_history=False)
            cubes_with_diffusive_material.append(neighbour_cube)
                        
                
                
                
    return cubes_with_diffusive_material

    
    

                    
            
            
            
            
            