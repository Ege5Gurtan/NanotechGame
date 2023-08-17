def create_grid(num_x,num_y,num_z,cube_size=1):
    # Parameters
    #num_x = 5  # Number of cubes in the x-direction
    #num_y = 3  # Number of cubes in the y-direction
    #num_z = 4  # Number of cubes in the z-direction
    #cube_size = 1.0  # Size of each cube
    
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    
    # Create cubes in a grid
    for i in range(num_x):
        for j in range(num_y):
            for k in range(num_z):
                bpy.ops.mesh.primitive_cube_add(size=cube_size, enter_editmode=False, location=(i * cube_size, j * cube_size, k * cube_size))

    # Update the scene
    bpy.context.view_layer.update()

