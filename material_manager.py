import bpy
import os
import importlib.util


def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def delete_all_materials():
    material_names = list(bpy.data.materials.keys())
    for material_name in material_names:
        bpy.data.materials.remove(bpy.data.materials[material_name], do_unlink=True)    

def create_material(material_name,R,G,B,A):
    new_material = bpy.data.materials.new(name=material_name)
    new_material.use_nodes = True
    principled_bsdf_node = new_material.node_tree.nodes["Principled BSDF"]
    principled_bsdf_node.inputs["Base Color"].default_value = (R,G,B,A)
    return new_material

def assign_material(obj,material_to_be_assigned):
    obj.data.materials.clear()
    obj.data.materials.append(material_to_be_assigned)


#grid_manager = include_module('grid_manager.py')
#grid = grid_manager.create_grid(2,3,4,cube_size=1)
#surface =  grid.select_surface_xz(0)
#material = create_material('test_material',1,0,0,0)
#for i in surface:
#    assign_material(i,material)
