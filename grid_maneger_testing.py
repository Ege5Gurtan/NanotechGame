def grid_tester():
    #test case 1:
    #num_x=num_y=num_z
    cube_size = 3
    for i in range(2,5):
        create_grid(i,i,i,cube_size=cube_size)
    
    #test case 2:
    #num_z>num_y>num_x
    create_grid(3,4,5,cube_size=cube_size)
    
    #test case 3:
    #num_x>num_y>num_z
    create_grid(4,3,2,cube_size=cube_size)
    
    #test case 4:
    #num_y>num_x>num_z
    create_grid(4,6,2,cube_size=cube_size)
    
    #test case 5:
    #num_z>num_x>num_y
    create_grid(4,3,6,cube_size=cube_size)
    
    #test case 6:
    #num_z>num_x=num_y
    create_grid(3,3,6,cube_size=cube_size)
    
    #test case 7:
    #num_x>num_y=num_z
    create_grid(4,3,3,cube_size=cube_size)
    
    #test case 8:
    #num_y>num_x=num_z
    create_grid(3,6,3,cube_size=cube_size)
    
    print('all tests have passed!')