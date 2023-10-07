import bpy
import importlib.util
import subprocess
import sys
import pandas as pd
import os
import numpy as np
import string

input_csv = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\dual_damascene_example\stack_description.csv"


material_csv = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\dual_damascene_example\material.csv"



def generate_array(length):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    result = []

    for i in range(length):
        letters = ''
        for j in range(3):
            letters += alphabet[i % 26]
            i //= 26
        result.append(letters)
    result.sort()
    return result



def create_scene(new_scene_name):
    bpy.ops.scene.new(type='FULL_COPY')
    created_scene.name = new_scene_name
    return created_scene

def build_stack(input_csv,material_csv='',construction_scene=None,animate=False):

    ## optional: material.csv

    #animate = True
    animation_starting_frame = 30
    num_frames_per_operation = 10
    frame_extension = 150


    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

    # Clear all objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Clear all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

    def include_module(module_path):
        spec = importlib.util.spec_from_file_location("my_module", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    gm = include_module('grid_manager.py')
    mm = include_module('material_manager.py')
    pm = include_module('process_manager.py')
    am = include_module('animation_manager.py')

    class Grid_Properties:
        def __init__(self):
            self.default_grid_size_x = 5
            self.default_grid_size_y = 5
            self.cube_size = 10

    class Materials:
        def __init__(self,use_material_df=False,df=''):
            self.material_dict = {
             'Si': mm.create_material('Si',0.5,0.5,0.5,1),
             'SiO2': mm.create_material('SiO2',1,0,0,1),
             'resist': mm.create_material('resist',0,1,0,1),
             'exposed': mm.create_material('exposed',1,0.014,0.998,1),
             'Nitride': mm.create_material('Nitride',0,0,0,1),
             'Cu':  mm.create_material('Cu',1,0.5,0.5,1),
             'Au':mm.create_material('Au',1,1,0,1),
             'ILD':mm.create_material('ILD',0.2,0.2,1,1),
             'IMD':mm.create_material('IMD',0,0,0.6,1),
            }
            if use_material_df:
                for i in range(len(df)):
                    material_name = df.loc[i, "Material"]
                    for material in bpy.data.materials:
                        if material_name == material.name:
                            bpy.data.materials.remove(material)
                    r =  float(df.loc[i, "R"])
                    g = float(df.loc[i, "G"])
                    b = float(df.loc[i, "B"])
                    a = float(df.loc[i, "A"])
                    self.material_dict[material_name] = mm.create_material(material_name,r,g,b,a)
                    

    class Deposit:
        def __init__(self,thickness,material_name,grid):
            self.material_class = Materials()
            self.material_to_deposit = material_class.material_dict[material_name]
            self.thickness = thickness
            self.grid = grid


    df = pd.read_csv(input_csv)
    df = df[~df['Process'].str.contains('%')]
    if not('Show_Step' in df.columns):
        df.insert(1,'Show_Step',[0]*(len(df.index)))
        
    def check_pattern_files(df):
        recorded_heights = []
        recorded_widths = []
        recorded_pattern_files = []
        
        pattern_files = df['Pattern'].dropna()
        for pattern_file in pattern_files:
                if os.path.exists(pattern_file):
                    pattern_file = pd.read_csv(pattern_file)
                    height = len(pattern_file)
                    width = len(pattern_file.columns)
                    recorded_heights.append(height)
                    recorded_widths.append(width)
                    recorded_pattern_files.append(pattern_file)
                else:
                    print('WARNING! Following pattern file does not exist: ',pattern_file)
        
        width = max(recorded_widths)
        height = max(recorded_heights)
        return width,height

    def is_number(string_value):
        try:
            number = float(string_value)
            return np.isfinite(number)
        except ValueError:
            return False

    grid_props = Grid_Properties()
    pattern_files = df['Pattern'].dropna()
    if len(pattern_files) == 0:
        estimated_grid_size_x, estimated_grid_size_y = grid_props.default_grid_size_x,grid_props.default_grid_size_y
    else: 
        estimated_grid_size_x, estimated_grid_size_y = check_pattern_files(df)
    estimated_grid_size_z = int(df['Thickness'].sum())


    grid = gm.create_grid(estimated_grid_size_x,estimated_grid_size_y,estimated_grid_size_z,cube_size=grid_props.cube_size)

    if os.path.exists(material_csv):
        material_df = pd.read_csv(material_csv)
        materials = Materials(use_material_df=True,df=material_df)
    else:
        materials = Materials()


    class Deposition():
        def __init__(self,cubes,material):
            self.cubes = cubes
            self.material =  material
            self.resist_type = None
            
    class Exposure():
        def __init__(self,cubes,material):
            self.cubes = cubes
            self.material = material

    class Development():
        def __init__(self,cubes):
            self.cubes = cubes
            
    class Etching():
        def __init__(self,cubes):
            self.cubes = cubes


    class Polishing():
        def __init__(self,cubes):
            self.cubes = cubes

    operations = []
    executed_processes = []
    if not(construction_scene == None):
        executed_processes = [construction_scene.name]
        show_executed_process = [0]
    
    for i in df.index.tolist():
        process = df.loc[i, "Process"]
        thickness = df.loc[i, "Thickness"]
        material_name =  df.loc[i, "Material"]
        resist_type = df.loc[i,'Resist_Type']
        pattern_file = df.loc[i,'Pattern']
        show_step = df.loc[i,'Show_Step']
        
        if isinstance(show_step,str):
            show_step = float(show_step)
        
        if '%' in process:
            continue
        
        if '#' in process:
            break

        if material_name in list(materials.material_dict.keys()):
            material_object = materials.material_dict[material_name]
        else:
            material_object = None
        
        if process == 'Deposit':
            deposited_cubes = pm.Deposit(int(thickness),grid,material_object)
            deposition  = Deposition(deposited_cubes,material_object)
            
            if isinstance(resist_type,str):
                deposition.resist_type = resist_type
            operations.append(deposition)        
            
        if process == 'Expose':
            last_operation = operations[-1]
            cubes_to_expose = last_operation.cubes
            if os.path.exists(pattern_file):
                pattern_df = pd.read_csv(pattern_file)
                if not(len(pattern_df) == estimated_grid_size_y): ### make heights of dfs equal if there is mismatch
                    difference = abs(len(pattern_df)-estimated_grid_size_y)
                    for _ in range(difference):
                        pattern_df.loc[pattern_df.shape[0]] = [np.nan]*df.shape[1]
                exposed_cubes = pm.Expose_Pattern_v2(cubes_to_expose,grid,materials.material_dict['exposed'],pattern_df)
            else:
                exposed_cubes = pm.Expose_Pattern(cubes_to_expose,grid,materials.material_dict['exposed'])
            exposure = Exposure(exposed_cubes,materials.material_dict['exposed'])
            operations.append(exposure)
            
        if process == 'Develop':
            last_operation = operations[-1] ##exposure
            last_operation_before_exposure = operations[-2] #resist deposition before exposure
            resist_type = last_operation_before_exposure.resist_type
            exposed_material = last_operation.material #exposed material
            developed_cubes = pm.Develop_Pattern(last_operation_before_exposure.cubes,exposed_material.name,grid,resist_type=resist_type)   
            development = Development(developed_cubes)
            operations.append(development)

        if process == 'Etch':
            if is_number(thickness):
                etched_cubes = pm.Etch([material_name],grid,etch_depth=int(thickness))
            else:
                etched_cubes = pm.Etch([material_name],grid)
            etching = Etching(etched_cubes)
            operations.append(etching)
            
            
        if process == 'Polish':
            polished_cubes = pm.Polish(material_name,grid)
            polishing = Polishing(polished_cubes)
            operations.append(polishing)
            
            
        
        if not(construction_scene == None) and show_step==1:
            executed_processes.append(process+'_'+str(i+2))
            bpy.ops.scene.new(type='FULL_COPY')
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.window.scene = construction_scene
            

    result = generate_array(len(executed_processes))
    
    if not(construction_scene == None) and not(animate):
        for process_name,scene,letter in zip(executed_processes,bpy.data.scenes.items(),result):
                scene[1].name = letter+'_'+process_name#chr(letter)+'_'+process_name
                for obj in scene[1].objects:
                    if obj.type == 'MESH':
                        if len(obj.data.materials) == 0:
                            obj.hide_viewport = True
                            obj.hide_render = True
                    
    
    
    bpy.ops.object.select_all(action='DESELECT')
    
    if animate or construction_scene == None:        
        all_cubes = []
        for operation in operations:
            all_cubes = all_cubes + operation.cubes
        

        all_cubes = list(set(all_cubes))
        all_total_frames = []
        for cube in all_cubes:
            animation_material = mm.create_material('animation',0,0,0,1)
            mm.assign_material(cube,animation_material,grid,add_to_history=False)
            cube_history = grid.cube_history[cube]    
            
            animated_cube = am.Cube_Animation(cube,animation_material,cube_history)
            total_frames = animated_cube.animate_all_states(animation_starting_frame,num_frames_per_operation)
            all_total_frames.append(total_frames)

        grid.hide_empty_cubes()

        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        bpy.context.scene.frame_end = total_frames + frame_extension
        bpy.ops.screen.animation_play()
        #import pdb;pdb.set_trace();
    else:
        grid.hide_empty_cubes()


import pickle   
import cProfile
import pstats
input_csv = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\example_inputs_1\stack_description.csv"
material_csv = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\example_inputs_1\material.csv"
#material_csv= ''


all_scenes = bpy.data.scenes
construction_scene = bpy.data.scenes.items()[0][1]
construction_scene.name = 'construction_scene'
for scene in all_scenes:
    if not(scene.name == construction_scene.name):
        bpy.data.scenes.remove(scene)
    
with cProfile.Profile() as profile:
    build_stack(input_csv,material_csv=material_csv,construction_scene=construction_scene,animate=True)


#scene_to_copy = bpy.data.scenes.get("Scene")
#new_scene = bpy.data.scenes.new(name='new scene')



results = pstats.Stats(profile)
results.sort_stats(pstats.SortKey.TIME)
#results.sort_stats(pstats.SortKey.CUMULATIVE)
#results.sort_stats(pstats.SortKey.FILENAME)
results.dump_stats('dual_damascene3.prof')
results.print_stats(20)

