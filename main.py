import bpy
import importlib.util
import subprocess
import sys
import pandas as pd
import os
import numpy as np

input_csv = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\example_inputs_1\stack_description.csv"

animate = False
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
    def __init__(self):
        self.material_dict = {
         'Si': mm.create_material('Si',0.5,0.5,0.5,1),
         'SiO2': mm.create_material('SiO2',1,0,0,1),
         'resist': mm.create_material('resist',0,1,0,1),
         'exposed': mm.create_material('exposed',0,0,1,1),
         'Nitride': mm.create_material('Nitride',0,0,0,1),
         'Au':mm.create_material('Au',1,1,0,1),
        }


class Deposit:
    def __init__(self,thickness,material_name,grid):
        self.material_class = Materials()
        self.material_to_deposit = material_class.material_dict[material_name]
        self.thickness = thickness
        self.grid = grid


df = pd.read_csv(input_csv)
df = df[~df['Process'].str.contains('%')]

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


grid_props = Grid_Properties()
pattern_files = df['Pattern'].dropna()
if len(pattern_files) == 0:
    width, height = grid_props.default_grid_size_x,grid_props.default_grid_size_y
else: 
    width, height = check_pattern_files(df)
estimated_grid_size_z = int(df['Thickness'].sum())


grid = gm.create_grid(width,height,estimated_grid_size_z,cube_size=grid_props.cube_size)
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
for i in range(len(df)):
    process = df.loc[i, "Process"]
    thickness = df.loc[i, "Thickness"]
    material_name =  df.loc[i, "Material"]
    resist_type = df.loc[i,'Resist_Type']
    pattern_file = df.loc[i,'Pattern']
    
    if '%' in process:
        continue

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
            if not(len(pattern_df) == height): ### make heights of dfs equal if there is mismatch
                difference = abs(len(pattern_df)-height)
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
        etched_cubes = pm.Etch([material_name],grid)
        etching = Etching(etched_cubes)
        operations.append(etching)
        
    if process == 'Polish':
        polished_cubes = pm.Polish(material_name,grid)
        polishing = Polishing(polished_cubes)
        operations.append(polishing)



if animate:        
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

else:
    grid.hide_empty_cubes()
    
        