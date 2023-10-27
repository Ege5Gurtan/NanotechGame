import bpy
import importlib.util


def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mm = include_module('material_manager.py')

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
    
    
def clear_materials():
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)
        
def clear_meshes():
    # Clear all objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()

    # Clear all meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

def clear_scenes():
    all_scenes = bpy.data.scenes
    for scene in all_scenes:
        if len(all_scenes) == 1:
            break
        else:
            bpy.data.scenes.remove(scene)

def grid_column_to_cubes(reference_cube_object,grid_column):
    for grid_cube in grid_column:
        if not(grid_cube.material == None):
            copy = reference_cube_object.copy()
            copy.data = reference_cube_object.data.copy()
            if grid_cube.is_exposed:
                material = mm.get_material_object('exposed')
            else:
                material = mm.get_material_object(grid_cube.material)
            copy.data.materials.append(material)
            copy.location.x = grid_cube.location[0]
            copy.location.y = grid_cube.location[1]
            copy.location.z = grid_cube.location[2]
            bpy.context.collection.objects.link(copy)
    
    
def grid_elements_to_cubes(grid_elements):
    dummy_cube = grid_elements[0]
    bpy.ops.mesh.primitive_cube_add(size=10, enter_editmode=False, location=dummy_cube.location)
    ob = bpy.context.object
    
    for grid_cube in grid_elements:
        if not(grid_cube.material == None):
            copy = ob.copy()
            copy.data = ob.data.copy()
            material = mm.get_material_object(grid_cube.material)
            copy.data.materials.append(material)
            copy.location.x = grid_cube.location[0]
            copy.location.y = grid_cube.location[1]
            copy.location.z = grid_cube.location[2]
            bpy.context.collection.objects.link(copy)
    bpy.data.objects.remove(ob)         
    bpy.context.view_layer.update()
    
def build_cubes(operations):
    cubes_to_build = []
    for operation in operations:
        cubes_to_build = operation.cubes+cubes_to_build
    cubes_to_build = list(set(cubes_to_build))
    grid_elements_to_cubes(cubes_to_build)

def create_scene(new_scene_name):
    bpy.ops.scene.new(type='FULL_COPY')
    created_scene.name = new_scene_name
    return created_scene