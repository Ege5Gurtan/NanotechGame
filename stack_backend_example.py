import bpy
import importlib.util
import subprocess
import sys

def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gm = include_module('grid_manager.py')
mm = include_module('material_manager.py')
pm = include_module('process_manager.py')
am = include_module('animation_manager.py')


grid = gm.create_grid(5,5,10,cube_size=10)

si_material = mm.create_material('SI',0.5,0.5,0.5,1)
sio2_material = mm.create_material('SIO2',1,0,0,1)
resist_material = mm.create_material('RESIST',0,1,0,1)
exposed_material = mm.create_material('EXPOSED',0,0,1,1)
nitride_material = mm.create_material('nitride',0,0,0,1)
gold_material = mm.create_material('gold',1,1,0,1)
animation_material = mm.create_material('animation',0,0,0,1)


si_cubes = pm.Deposit(1,grid,si_material)
sio2_cubes = pm.Deposit(2,grid,sio2_material)
nitride_cubes = pm.Deposit(1,grid,nitride_material)
resist_layer_cubes = pm.Deposit(1,grid,resist_material)
exposed_cubes = pm.Expose_Pattern(resist_layer_cubes,grid,exposed_material)
developed_cubes = pm.Develop_Pattern(resist_layer_cubes,exposed_material.name,grid,resist_type='positive')
all_cubes = si_cubes+sio2_cubes+nitride_cubes+resist_layer_cubes+exposed_cubes+developed_cubes

etched_cubes_nitride = pm.Etch(['nitride'],grid)
etched_cubes_sio2 = pm.Etch(['SIO2'],grid)
etched_resist = pm.Etch(['RESIST'],grid)

gold_cubes = pm.Deposit(5,grid,gold_material)
polished_cubes = pm.Polish('gold',grid)


all_cubes = all_cubes+etched_resist+etched_cubes_nitride+etched_cubes_sio2+gold_cubes+polished_cubes
all_cubes = list(set(all_cubes))
all_total_frames = []
for cube in all_cubes:
    animation_material = mm.create_material('animation',0,0,0,1)
    mm.assign_material(cube,animation_material,grid,add_to_history=False)
    cube_history = grid.cube_history[cube]
    animated_cube = am.Cube_Animation(cube,animation_material,cube_history)
    total_frames = animated_cube.animate_all_states(30,10)
    all_total_frames.append(total_frames)


if bpy.context.screen.is_animation_playing:
    bpy.ops.screen.animation_cancel(restore_frame=False)

bpy.context.scene.frame_end = total_frames + 150
bpy.ops.screen.animation_play()
