import bpy



# Create a new material
obj = bpy.data.objects["Cube"]


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

delete_all_materials()
new_mat = create_material('sp',1,0,0,0)
assign_material(obj,new_mat)
