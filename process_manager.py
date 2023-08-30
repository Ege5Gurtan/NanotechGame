import bpy
import importlib.util
import subprocess
import sys
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('WebAgg')
from matplotlib.backend_bases import PickEvent


colors = ['red', 'blue', 'green', 'purple', 'orange','red', 'blue', 'green', 'purple', 'orange',
'red', 'blue', 'green', 'purple', 'orange','red', 'blue', 'green', 'purple', 'orange',
'red', 'blue', 'green', 'purple', 'orange']



def install(package):
    #Allows you to install external python packages inside blender.
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    ##Example usage: install('pandas')
    

def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

gm = include_module('grid_manager.py')
mm = include_module('material_manager.py')

def check_if_cube_has_material(cube):
    if hasattr(cube,"data") and hasattr(cube.data,"materials") and (len(cube.data.materials) > 0):
        return True
    else:
        return False

def Deposit(thickness,grid,material):
    deposited_cubes = []
    for column_index in range(0,grid.grid_num_columns):
        column = grid.select_column(column_index)
        number_of_deposited_cubes = 0
        for cube in column:
            cube_index = grid.cube_indices[cube]
            grid_cube = gm.Grid_Cube(grid,cube_index)
            
            if number_of_deposited_cubes < thickness:
                
                deposit = False
                
                #check if minus z neighbour of the cube has material assigned
                bottom_has_material = check_if_cube_has_material(grid_cube.neighbour_minus_z_cube)
                
                #check if the cube has already a material assigned
                itself_has_material = check_if_cube_has_material(cube)
                
                if bottom_has_material and not(itself_has_material):
                    deposit = True
                elif grid_cube.neighbour_minus_z_cube == None and not(itself_has_material):
                    deposit = True
                
                if deposit:
                    mm.assign_material(cube,material)
                    number_of_deposited_cubes +=1
                    deposited_cubes.append(cube)
    return deposited_cubes
                    
grid = gm.create_grid(5,5,5,cube_size=10)
test_material = mm.create_material('SI',1,0,0,0)
test_material2 = mm.create_material('RESIST',1,1,0,0)
Deposit(3,grid,test_material)
resist_layer_cubes = Deposit(1,grid,test_material2)

#install('tornado')
x_points = []
y_points = []
for i in resist_layer_cubes:
    point = gm.Grid_Cube.get_cube_center_point(i)
    x_points.append(point[0])
    y_points.append(point[1])



plt.close('all')

colors = ['red', 'blue', 'green', 'purple', 'orange','red', 'blue', 'green', 'purple', 'orange',
'red', 'blue', 'green', 'purple', 'orange','red', 'blue', 'green', 'purple', 'orange',
'red', 'blue', 'green', 'purple', 'orange']

fig, ax = plt.subplots(nrows=1,ncols=1)
scatter = ax.scatter(x_points, y_points, c=colors, picker=True)

def onpick(event):
    if isinstance(event, PickEvent):
        ind = event.ind[0]  # Get the index of the selected point
        current_color = scatter.get_facecolor()[ind]
        # Change the color of the selected point
        new_color = 'yellow' if current_color == 'red' else 'red'
        scatter.set_facecolor(colors[:ind] + [new_color] + colors[ind+1:])
        fig.canvas.draw_idle()

fig.canvas.mpl_connect('pick_event', onpick)



plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Interactive Scatter Plot')
plt.show()




