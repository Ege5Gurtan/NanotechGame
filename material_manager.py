import bpy
import os
import importlib.util

def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def set_material_color(material,R,G,B,A):
    principled_bsdf_node = material.node_tree.nodes["Principled BSDF"]
    principled_bsdf_node.inputs["Base Color"].default_value = (R,G,B,A)

def create_material(material_name,R,G,B,A):
    new_material = bpy.data.materials.new(name=material_name)
    new_material.use_nodes = True
    principled_bsdf_node = new_material.node_tree.nodes["Principled BSDF"]
    principled_bsdf_node.inputs["Base Color"].default_value = (R,G,B,A)
    return new_material

def assign_material(obj,material_to_be_assigned,grid,add_to_history=True):
    obj.data.materials.clear()
    obj.data.materials.append(material_to_be_assigned)
    if add_to_history:
        grid.cube_history[obj].append(material_to_be_assigned)

def check_if_cube_has_material(cube):
    if hasattr(cube,"data") and hasattr(cube.data,"materials") and (len(cube.data.materials) == 1):
        return True
    else:
        return False

def check_if_cube_has_given_material(obj,material_to_check):
    #print(obj.data.materials[0].name)
    if obj.data.materials[0].name in material_to_check:
        return True
    else:
        return False

def get_material_name(obj):
    if check_if_cube_has_material(obj):
        return obj.data.materials[0].name
    else:
        return None
    
def material_to_rgba(material):
    principled_bsdf_material = material.node_tree.nodes.get("Principled BSDF")
    r = principled_bsdf_material.inputs["Base Color"].default_value[0]
    g = principled_bsdf_material.inputs["Base Color"].default_value[1]
    b = principled_bsdf_material.inputs["Base Color"].default_value[2]
    a = principled_bsdf_material.inputs["Base Color"].default_value[3]
    return r,g,b,a
    
    
#grid_manager = include_module('grid_manager.py')
#grid = grid_manager.create_grid(2,3,4,cube_size=1)
#surface =  grid.select_surface_xz(0)
#material = create_material('test_material',1,0,0,0)
#for i in surface:
#    assign_material(i,material)

