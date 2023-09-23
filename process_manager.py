import bpy
import importlib.util

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


def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gm = include_module('grid_manager.py')
mm = include_module('material_manager.py')
um = include_module('ui_manager.py')

def Deposit(thickness,grid,material):
    deposited_cubes = []
    for column_index in range(0,grid.grid_num_columns):
        column = grid.select_column(column_index)
        number_of_deposited_cubes = 0
        for cube in column:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
            cube_index = grid.cube_indices[cube]
            grid_cube = gm.Grid_Cube(grid,cube_index)
            
            if number_of_deposited_cubes < thickness:
                
                deposit = False
                
                #check if minus z neighbour of the cube has material assigned
                bottom_has_material = mm.check_if_cube_has_material(grid_cube.neighbour_minus_z_cube)
                
                #check if the cube has already a material assigned
                itself_has_material = mm.check_if_cube_has_material(cube)
                
                if bottom_has_material and not(itself_has_material):
                    deposit = True
                elif grid_cube.neighbour_minus_z_cube == None and not(itself_has_material):
                    deposit = True
                
                if deposit:
                    mm.assign_material(cube,material,grid,add_to_history=False)
                    number_of_deposited_cubes +=1
                    deposited_cubes.append(cube)
                    grid.cube_history[cube][-1] = material
                    
    
                    
    
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
        


def Etch(materials_to_etch,grid):
    etched_cubes = []
    #materials_to_etch = ['nitride','SIO2']
    #Etch(materials_to_etch,grid)
    for column in grid.all_columns:
        column_cubes = grid.all_columns[column]
        for cube in column_cubes[::-1]:
            grid.cube_history[cube].append(grid.cube_history[cube][-1])
            cube_index = grid.cube_indices[cube]
            grid_cube = gm.Grid_Cube(grid,cube_index)
            ##if cube itself has material to be etched and it above neighbour is empty
            top_neighbour_cube = grid_cube.neighbour_z_cube 
            if not(top_neighbour_cube==None):
                top_has_material = mm.check_if_cube_has_material(top_neighbour_cube)
                cube_has_material =  mm.check_if_cube_has_material(cube)
                name = mm.get_material_name(cube)
                if not(top_has_material) and cube_has_material:
                    for material_name in materials_to_etch:
                        if material_name in name:                            
                            cube.data.materials.clear()
                            etched_cubes.append(cube)
                            grid.cube_history[cube][-1] = 'empty'

                            
    
    return etched_cubes
                            


def Polish(material_to_polish,grid):
    polished_cubes = []
    for xy_surface in reversed(grid.surfaces_xy):
        surface_cubes = grid.surfaces_xy[xy_surface]
        found_materials = []
        for cube in surface_cubes:
            material =  mm.get_material_name(cube)
            found_materials.append(material)
        
        #import pdb;pdb.set_trace();
        found_materials_without_none = [item for item in found_materials if item is not None]
        layer_to_remove = all(material_to_polish in item for item in found_materials_without_none)
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
