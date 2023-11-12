import bpy
import importlib

def include_module(module_path):
    spec = importlib.util.spec_from_file_location("my_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

mm = include_module('material_manager.py')

def add_appear_animation(obj,start_frame,end_frame):
    try:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')

        # Set the initial scale to be very small (fully hidden)
        obj.scale = (0.001, 0.001, 0.001)

        # Create a keyframe for scale at frame 1
        obj.keyframe_insert(data_path='scale', frame=start_frame)

        # Set the final scale to its original scale (fully visible)
        obj.scale = (1, 1, 1)

        # Create keyframes for scale at the desired fade-in duration
        obj.keyframe_insert(data_path='scale', frame=end_frame)
    except:
        print(obj,'has problems')
    # Set the end frame of the animation
    
def add_disappear_animation(obj,start_frame,end_frame):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set the initial scale to be very small (fully hidden)
    obj.scale = (1, 1, 1)

    # Create a keyframe for scale at frame 1
    obj.keyframe_insert(data_path='scale', frame=start_frame)

    # Set the final scale to its original scale (fully visible)
    obj.scale = (0.001, 0.001, 0.001)

    # Create keyframes for scale at the desired fade-in duration
    obj.keyframe_insert(data_path='scale', frame=end_frame)
    
def material_appear_animation(material,start_frame,end_frame):

    #material = obj.active_material
    shader_node = material.node_tree.nodes["Principled BSDF"]
    
    #transparent
    material.blend_method='BLEND'
    shader_node.inputs["Alpha"].default_value = 0
    material.keyframe_insert(data_path="blend_method",frame=start_frame)
    shader_node.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=start_frame)
    
    #opaque
    material.blend_method='OPAQUE'
    shader_node.inputs["Alpha"].default_value = 1
    material.keyframe_insert(data_path="blend_method",frame=end_frame)
    shader_node.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=end_frame)
    

def change_color_animation(material,start_frame,end_frame,final_color):
    principled_bsdf = material.node_tree.nodes.get("Principled BSDF")
    f_r, f_g, f_b, f_a = final_color[0],final_color[1],final_color[2],final_color[3]
    principled_bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=start_frame)
    principled_bsdf.inputs["Base Color"].default_value = (f_r,f_g,f_b,f_a)
    principled_bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=end_frame)
        
def material_disappear_animation(material,start_frame,end_frame):
    shader_node = material.node_tree.nodes["Principled BSDF"]
    
    #opaque
    material.blend_method='BLEND'
    shader_node.inputs["Alpha"].default_value = 1
    material.keyframe_insert(data_path="blend_method",frame=start_frame)
    shader_node.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=start_frame)
    
    #transparent
    material.blend_method='BLEND'
    shader_node.inputs["Alpha"].default_value = 0
    material.keyframe_insert(data_path="blend_method",frame=end_frame)
    shader_node.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=end_frame)
   
def material_transition_animation(cubes,material_list,frame_list,grid):
    r,g,b,a = mm.material_to_rgba(material_list[0])
    animation_material = mm.create_material('animation_material',r,g,b,a)
    shader_node_animation_material = animation_material.node_tree.nodes["Principled BSDF"]
    
    for cube in cubes:
        cube.data.materials.clear()
        mm.assign_material(cube,animation_material,grid,add_to_history=False)
    
    for current_material,current_frame in zip(material_list,frame_list):
        r,g,b,a = mm.material_to_rgba(current_material)
        shader_node_current_material = current_material.node_tree.nodes["Principled BSDF"]
        
        principled_bsdf = animation_material.node_tree.nodes.get("Principled BSDF")
        principled_bsdf.inputs["Base Color"].default_value = (r,g,b,a)
        
        
        animation_material.blend_method=current_material.blend_method
        shader_node_animation_material.inputs["Alpha"].default_value = shader_node_current_material.inputs["Alpha"].default_value
        
        principled_bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=current_frame)
        
        animation_material.keyframe_insert(data_path="blend_method",frame=current_frame)
        shader_node_animation_material.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=current_frame)

def material_transition_animation_v2(animation_material,material_list,frame_list,grid):
    shader_node_animation_material = animation_material.node_tree.nodes["Principled BSDF"]
    for current_material,current_frame in zip(material_list,frame_list):
        r,g,b,a = mm.material_to_rgba(current_material)
        shader_node_current_material = current_material.node_tree.nodes["Principled BSDF"]
        
        principled_bsdf = animation_material.node_tree.nodes.get("Principled BSDF")
        principled_bsdf.inputs["Base Color"].default_value = (r,g,b,a)
        
        animation_material.blend_method=current_material.blend_method
        shader_node_animation_material.inputs["Alpha"].default_value = shader_node_current_material.inputs["Alpha"].default_value
        
        principled_bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=current_frame)
        
        animation_material.keyframe_insert(data_path="blend_method",frame=current_frame)
        shader_node_animation_material.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=current_frame)
        
def animate_layer_cubes(layer_cubes,frame_duration,grid):
    for cube in layer_cubes:
        cube.data.materials.clear()
        material_list = grid.cube_history[cube]

        animation_material = mm.create_material('animation_material',0,0,0,1)
        mm.assign_material(cube,animation_material,grid,add_to_history=False)
        
        new_material_list = []
        counter=1
        
        first_time_appear = True
        for index,material in enumerate(material_list):
            current_frame = counter*frame_duration
            counter = counter +1
            
            #print(grid.cube_history[cube])
            #material is appearing from nothing
            if not(material_list[index]=='empty') and (material_list[index-1] == 'empty'):
                r,g,b,a = mm.material_to_rgba(material_list[index])
                #animation_material = mm.create_material('animation_material',r,g,b,a)
                #mm.assign_material(cube,animation_material,grid,add_to_history=False)
                material_appear_animation(animation_material,current_frame,current_frame+frame_duration)
            
            ##material is disappearing
            elif (material_list[index] == 'empty') and not(material_list[index-1] == 'empty'):
                r,g,b,a = mm.material_to_rgba(material_list[index-1])
                material_disappear_animation(animation_material,current_frame,current_frame+frame_duration)
            
            #material is changing color
            elif not(material_list[index] == 'empty') and not(material_list[index-1] == 'empty'):
                material_transition_animation_v2(animation_material,[material_list[index-1],material_list[index]],[current_frame,current_frame+frame_duration],grid)
                #r,g,b,a = mm.material_to_rgba(material_list[index])
                #change_color_animation(animation_material,current_frame,current_frame+frame_duration,[r,g,b,a])
                



class Cube_Animation:
    def __init__(self,cube,animation_material,cube_history):
        self.cube = cube
        self.material = animation_material
        self.states = []
        self.frames = []
        self.cube_history = cube_history
    
    def make_transparent(self):
        #transparent
        shader_node = self.material.node_tree.nodes["Principled BSDF"]
        self.material.blend_method='BLEND'
        shader_node.inputs["Alpha"].default_value = 0
    
    def make_opaque(self,fade_out=False):
        shader_node = self.material.node_tree.nodes["Principled BSDF"]
        self.material.blend_method='OPAQUE'
        shader_node.inputs["Alpha"].default_value = 1
        
    def set_color(self,r,g,b,a):
        mm.set_material_color(self.material,r,g,b,a)
    
    def save_state(self):
        shader_node = self.material.node_tree.nodes["Principled BSDF"]
        r,g,b,a = mm.material_to_rgba(self.material)
        blend_method = self.material.blend_method
        shader_alpha = shader_node.inputs["Alpha"].default_value
        state = {'r':r,'g':g,'b':b,'a':a,'blend_method':blend_method,'shader_alpha':shader_alpha}
        self.states.append(state)
        
    def animate_between_states(self,state1,state2,frame1,frame2):
        shader_node_animation_material = self.material.node_tree.nodes["Principled BSDF"]
        principled_bsdf = self.material.node_tree.nodes.get("Principled BSDF")
        
        self.material.blend_method=state1['blend_method']
        principled_bsdf.inputs["Base Color"].default_value = (state1['r'],state1['g'],state1['b'],state1['a'])
        shader_node_animation_material.inputs["Alpha"].default_value = state1['shader_alpha']
        
        principled_bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=frame1)
        self.material.keyframe_insert(data_path="blend_method",frame=frame1)
        shader_node_animation_material.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=frame1)
        
        self.material.blend_method=state2['blend_method']
        principled_bsdf.inputs["Base Color"].default_value = (state2['r'],state2['g'],state2['b'],state2['a'])
        shader_node_animation_material.inputs["Alpha"].default_value = state2['shader_alpha']
        
        principled_bsdf.inputs["Base Color"].keyframe_insert(data_path="default_value", frame=frame2)
        self.material.keyframe_insert(data_path="blend_method",frame=frame2)
        shader_node_animation_material.inputs["Alpha"].keyframe_insert(data_path="default_value", frame=frame2)
        
    def make_opaque_before_fade_out(self):
        shader_node = self.material.node_tree.nodes["Principled BSDF"]
        self.material.blend_method='BLEND'
        shader_node.inputs["Alpha"].default_value = 1
    
    def animate_all_states(self,frame_duration,starting_frame):
        previous_event = None
        for event_index,event in enumerate(self.cube_history):
            
            if event == 'empty' and previous_event==None:
                self.make_transparent()
                self.save_state()
                self.save_state()
                
            elif event == 'empty' and not(previous_event == 'empty') and not(previous_event==None):
                
                self.make_opaque_before_fade_out()
                self.save_state()
                self.make_transparent()
                self.save_state()
            
            elif event == 'empty' and previous_event == 'empty': 
                self.save_state()
                self.save_state()
            
            elif type(event).__name__ == 'Material':
                r,g,b,a = mm.material_to_rgba(event)
                self.set_color(r,g,b,a)
                self.save_state()
                self.make_opaque()
                self.save_state()
            
            previous_event = event

        #frame_duration = 100
        #current_frame = 1
        for state_index,state in enumerate(self.states):
            if state_index == len(self.states)-1:
                break
            self.animate_between_states(self.states[state_index],self.states[state_index+1],starting_frame,starting_frame+frame_duration)
            starting_frame = frame_duration + starting_frame
        
        return starting_frame
                


            
            
            
            
            
            
            
    
    
        

        
        
