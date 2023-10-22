import importlib.util
import pandas as pd
import bpy
import threading
import concurrent.futures
import os
import sys
#os.system('cls')



def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ifm = include_module('input_file_manager.py')
pm = include_module('process_manager.py')
gm = include_module('grid_manager.py')
sm = include_module('scene_manager.py')
stm = include_module('stack_manager.py')
sm.clear_scenes()
sm.clear_materials()
sm.clear_meshes()

number_of_cores_to_use = 4


def construct_cubes_using_threading(current_grid_columns):
    bpy.ops.mesh.primitive_cube_add(size=10, enter_editmode=False, location=(0,0,0))
    ob = bpy.context.object
    threads = []
    arguments = []
    for grid_col in current_grid_columns:
        arguments.append((ob,current_grid_columns[grid_col]))
    
    for args in arguments:
        thread = threading.Thread(target= sm.grid_column_to_cubes,args=args)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()   
    bpy.data.objects.remove(ob)    

def construct_cubes_using_multiprocessing(current_grid_columns,max_thread_number):
    bpy.ops.mesh.primitive_cube_add(size=10, enter_editmode=False, location=(0,0,0))
    ob = bpy.context.object
    with concurrent.futures.ThreadPoolExecutor(max_thread_number) as executor:
        arguments = []
        for grid_col in current_grid_columns:
            arguments.append((ob,current_grid_columns[grid_col]))
        
        results = []
        for arg1,arg2 in arguments:
            result = executor.submit(sm.grid_column_to_cubes,arg1,arg2)
            results.append(result)
        
    for result in results:
        result.result()
    
    
    bpy.data.objects.remove(ob)  
        
def construct_scenes_using_multiprocessing(current_grid,name_prefix,process,new_scene):
    
    bpy.context.window.scene  = new_scene
    current_grid_columns = current_grid.grid_all_columns
    construct_cubes_using_multiprocessing(current_grid_columns,number_of_cores_to_use)
    
    

def build_stack(stack_csv_path,material_csv_path=''):
    df = pd.read_csv(stack_csv_path)
    if material_csv_path == '':
        material_csv_path = ifm.get_material_file_path(df)
    height,width = ifm.get_grid_xy_dimension_from_patterns(df)
    active_processes_df = ifm.get_active_processes_df(df)
    estimated_stack_thickness = int(active_processes_df[active_processes_df['Process']=='Deposit']['Thickness'].sum())+1

    grid_props = gm.Grid_Properties()
    grid = gm.create_grid_v2(width,height,estimated_stack_thickness,cube_size=grid_props.cube_size)
    processes,grid_states = stm.construct_active_processes(df,grid,material_csv=material_csv_path)
    
    scene_name_prefixes = sm.generate_array(len(grid_states))
    
    
    for current_grid,name_prefix,process in zip(grid_states,scene_name_prefixes,processes):

        new_scene = bpy.data.scenes.new(name_prefix+'_'+process.name+'_'+str(process.order))
        bpy.context.window.scene  = new_scene
        current_grid_columns = current_grid.grid_all_columns
        construct_cubes_using_multiprocessing(current_grid_columns,4)
        
        bpy.context.view_layer.update()            
        bpy.ops.object.select_all(action='DESELECT')
        
        

if __name__ == '__main__':
    stack_csv_path = sys.argv[4]
#stack_csv_path = r"C:\Users\egurtan\Desktop\NEW_TEST\NanotechGame-main\MOSFET\stack_description_mosfet.csv"

print('Using the following stack description file')
print(stack_csv_path)

build_stack(stack_csv_path)
folder_path = os.path.split(stack_csv_path)[0]
file_name_with_extension = os.path.split(stack_csv_path)[1]
filename, ext = os.path.splitext(file_name_with_extension)
output_file_name_blender = os.path.join(folder_path,filename+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=output_file_name_blender)

print('stack building is complete!')


###########for performance profiling
#import cProfile
#import pstats
#with cProfile.Profile() as profile:
#    build_stack(stack_csv_path,material_csv_path = material_csv_path)

#scene_to_copy = bpy.data.scenes.get("Scene")
#new_scene = bpy.data.scenes.new(name='new scene')

#results = pstats.Stats(profile)
#build_stack(input_csv,material_csv=material_csv,construction_scene=construction_scene,animate=False)
#results.sort_stats(pstats.SortKey.TIME)
#results.print_stats(20)
#print('done')

#build_stack(sys.argv[1])

#output_file_name_blender = 
#bpy.ops.wm.save_as_mainfile(filepath=file_path)

