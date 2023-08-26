import bpy

material_names = list(bpy.data.materials.keys())
for material_name in material_names:
    bpy.data.materials.remove(bpy.data.materials[material_name], do_unlink=True)
    print(f"Material '{material_name}' deleted.")

# Create a new material
material_name = "ColoredMaterial32"
new_material = bpy.data.materials.new(name=material_name)
new_material.use_nodes = True

principled_bsdf_node = new_material.node_tree.nodes["Principled BSDF"]

principled_bsdf_node.inputs["Base Color"].default_value = (0,1,0,1)



obj = bpy.data.objects["Cube"]
obj.data.materials.clear()
#material_index = obj.data.materials.find(material_name)
#print(material_index)
#obj.data.materials.pop(0)
obj.data.materials.append(new_material)

