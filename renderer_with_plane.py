import glfw
import numpy as np
import glm
import moderngl
import cv2 as cv

from extract_file import get_vectors, get_vertex_attributes
from utils import map_mouse_to_sphere, transform_triangles
from calc_points import make_img_np

path = "Files/Enterprise.stl"

#mouse events
prev_mouse_x = 0.0
prev_mouse_y = 0.0
start_trackball = glm.vec3(0.0, 0.0, 0.0)

left_click = False
right_click = False

mouse_scroll = 0.0
zoom = 1.0

#modes (model or plane)
mode_model = True
mode_slice = False

#model positionsppp
model_pos = glm.vec3(0.0, 0.0, 0.0)
model_ori = glm.quat(1.0, 0.0, 0.0, 0.0) 
current_transformed_tris = []

#slicing
slice_plane_pos = glm.vec3(0.0, 0.0, 0.0)
slice_plane_eq = glm.vec4(0.0, 0.0, 0.0, 0.0)
slice_plane_ori = glm.quat(1.0, 0.0, 0.0, 0.0)

def click_callback(window, button, action, mod):
    global left_click, right_click, start_trackball
    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            right_click = True
            x, y = glfw.get_cursor_pos(window)
            w, h = glfw.get_window_size(window)
            start_trackball = map_mouse_to_sphere(x, y, w, h)
        if action == glfw.RELEASE:
            right_click = False
    elif button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            left_click = True
        if action == glfw.RELEASE:
            left_click = False

def scroll_callback(window, x_offset, y_offset):
    global mouse_scroll
    mouse_scroll = y_offset

def key_callback(window, key, scancode, action, mod):
    global mode_model, mode_slice, current_transformed_tris, slice_plane_ori
    if key == glfw.KEY_M and action == glfw.PRESS:
        mode_model = not mode_model
    if key == glfw.KEY_S and action == glfw.PRESS:
        mode_slice = not mode_slice

def get_slice_plane_eq():
    global slice_plane_pos, slice_plane_ori
    slice_plane_norm = slice_plane_ori * glm.vec3(0, 0, 1)
    slice_plane_norm = glm.normalize(slice_plane_norm)
    d = -glm.dot(slice_plane_norm, slice_plane_pos)
    return glm.vec4(slice_plane_norm, d)

def render(path="Files/enterprise.stl", cross_section=True):
    global prev_mouse_x, prev_mouse_y, start_trackball
    global mouse_scroll, zoom
    global left_click, right_click
    global model_pos, model_ori
    global mode_model, mode_slice, current_transformed_tris
    global slice_plane_pos, slice_plane_eq, slice_plane_ori

    if not glfw.init():
        raise Exception("GLFW can't be initialized")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(1200, 800, "ModernGL", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    ctx = moderngl.create_context()
    ctx.enable(moderngl.DEPTH_TEST)

    #just making sure the initial eqn is corrent
    slice_plane_eq = get_slice_plane_eq()

    # for blending
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    #avoids rendering inner faces of the model so it doesn't look weird
    ctx.enable(moderngl.CULL_FACE)

    ctx.clear(0.0, 0.0, 0.0, 1.0)

    current_transformed_tris = get_vectors(path=path)

    #mouse event stuff
    glfw.set_mouse_button_callback(window, click_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)

    tri = get_vertex_attributes(path)
    tri = np.array(tri, dtype='f4')

    plane_vertices = np.array([
        # pos
        -20.0, -20.0, 0.0,
         20.0, -20.0, 0.0,
        -20.0,  20.0, 0.0,

         20.0, -20.0, 0.0,
         20.0,  20.0, 0.0,
        -20.0,  20.0, 0.0
    ], dtype='f4')

    #shaders
    prog = ctx.program(vertex_shader = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 normal;
        out vec3 normal_out;
        out float dist_to_plane;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        uniform vec4 slice_plane; // (A, B, C, D) in plane Ax + By + Cz + D = 0

        void main() {
            vec4 world_pos = model * vec4(position, 1.0);
            gl_Position = projection * view * world_pos;
            normal_out = normal;
            
            dist_to_plane = dot(world_pos, slice_plane);
        }
        """,
        fragment_shader = """
        #version 330 core
        out vec4 outColor;
        in vec3 normal_out;
        in float dist_to_plane;

        uniform float dist_tolerance;
        uniform vec3 slice_color;

        void main() {
            if(abs(dist_to_plane) < dist_tolerance){
                outColor = vec4(slice_color, 1.0);
            } else {
                outColor = vec4(0.5 + normal_out * 0.5, 0.5);
            }
        }
        """
    )

    vbo = ctx.buffer(tri.tobytes())
    vao = ctx.vertex_array(
        prog,
        [
            (vbo, '3f 3f', 'position', 'normal'),
        ]
    )

    plane_prog = ctx.program(vertex_shader="""
        #version 330 core
        layout(location = 0) in vec3 pos;
        
        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;
        
        void main(){
            gl_Position = projection * view * model * vec4(pos, 1.0);
        }
        """,
        fragment_shader="""
        #version 330 core
        out vec4 outColor;
        uniform vec4 slice_color;

        void main(){
            outColor = slice_color;
        }
        """)

    plane_vbo = ctx.buffer(plane_vertices.tobytes())
    plane_vao = ctx.vertex_array(
        plane_prog,
        [
            (plane_vbo, '3f', 'pos'),
        ]
    )

    # Transformation Matrices (for model)
    model = glm.mat4(1.0)
    view = glm.lookAt(glm.vec3(20, 20, 20), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    projection = glm.perspective(glm.radians(45.0), 1200 / 800, 0.1, 100.0)

    prog['view'].write(np.array(view.to_list(), dtype='f4'))
    prog['projection'].write(np.array(projection.to_list(), dtype='f4'))
    prog['dist_tolerance'].write(np.array([0.01], dtype='f4'))
    prog['slice_color'].write(np.array([1.0, 1.0, 1.0], dtype='f4'))

    # Transformation Matrices (for model)
    plane_model = glm.mat4(1.0)
    plane_view = view
    plane_projection = projection

    plane_prog['view'].write(np.array(plane_view.to_list(), dtype='f4'))
    plane_prog['projection'].write(np.array(plane_projection.to_list(), dtype='f4'))

    redraw = False
    
    while not glfw.window_should_close(window):
        glfw.poll_events()

        ctx.clear(0.0, 0.0, 0.0, 1.0)

        mouse_x, mouse_y = glfw.get_cursor_pos(window)
        
        if left_click:
            dx = (mouse_x - prev_mouse_x)/50
            dy = (mouse_y - prev_mouse_y) /50

            # inverse matrix is the same as camera matrix (i.e. view from current perspective)
            # translate relative to camera's up & down
            inverse_m = glm.inverse(view)
            cam_right = glm.vec3(inverse_m[0])
            cam_up = glm.vec3(inverse_m[1])

            if mode_model:
                model_pos += dx * cam_right
                model_pos -= dy * cam_up

            if mode_slice:
                slice_plane_pos += dx * cam_right
                slice_plane_pos -= dy * cam_up
                slice_plane_eq = get_slice_plane_eq()

            if mode_slice != mode_model:
                redraw = True

        if right_click:
            x, y = glfw.get_cursor_pos(window)
            width, height = glfw.get_window_size(window)
            current_trackball = map_mouse_to_sphere(x, y, width, height)

            axis = glm.cross(start_trackball, current_trackball)

            if glm.length(axis) > 0.0001: # Check for non-zero length to avoid division by zero
                axis = glm.normalize(axis)
            else:
                axis = glm.vec3(0, 0, 0) # No rotation if axis is zero

            angle = glm.acos(glm.dot(start_trackball, current_trackball))
            angle *= 3      #determines rotation speed

            if glm.length(axis) > 0.0001 and abs(angle) > 0.0001: # Only rotate if there's a valid axis and angle
                # Create incremental quaternion for this frame's rotation
                rotation_quat = glm.angleAxis(angle, axis)

                if mode_model and mode_slice:
                    model_ori = rotation_quat * model_ori
                    slice_plane_ori = rotation_quat * slice_plane_ori

                     # 1. Temporarily shift slice_plane_pos so model_pos is the origin
                    relative_pos = slice_plane_pos - model_pos
                    # 2. Rotate this relative position
                    rotated_relative_pos = rotation_quat * relative_pos
                    # 3. Shift slice_plane_pos back relative to the new model_pos
                    slice_plane_pos = model_pos + rotated_relative_pos

                    model_ori = glm.normalize(model_ori)
                    slice_plane_ori = glm.normalize(slice_plane_ori)
                    
                    slice_plane_norm = slice_plane_ori * glm.vec3(0, 0, 1)
                    slice_plane_norm = glm.normalize(slice_plane_norm)
                    d = -glm.dot(slice_plane_norm, slice_plane_pos)
                    slice_plane_eq = glm.vec4(slice_plane_norm, d)

                elif mode_model:
                    # Accumulate the new rotation onto the existing model orientation
                    # This order (new_quat * old_quat) applies rotations in world space.
                    # For a "trackball" that orbits a central point, this usually feels natural.
                    model_ori = rotation_quat * model_ori

                    # Normalize the quaternion periodically to prevent floating-point drift
                    model_ori = glm.normalize(model_ori)
                    redraw = True

                elif mode_slice:
                    #do same thing for slicing plane
                    slice_plane_ori = rotation_quat * slice_plane_ori
                    slice_plane_ori = glm.normalize(slice_plane_ori)
                    
                    slice_plane_eq = get_slice_plane_eq()
                    redraw = True

            start_trackball = current_trackball

        model = glm.mat4(1.0)
        plane_model = glm.mat4(1.0)

        # scaling with mouse wheel
        if mouse_scroll != 0.0:
            if mode_model:
                scale = 1 + mouse_scroll / 50
                zoom *= scale
                if zoom < 0.001:
                    zoom = 0.001
                # redraw = True
            mouse_scroll = 0

        plane_model = glm.translate(plane_model, slice_plane_pos)
        plane_model = plane_model * glm.mat4_cast(slice_plane_ori)
        #NO SCALING FOR SLICING PLANE

        plane_prog['model'].write(np.array(plane_model.to_list(), dtype='f4'))
        plane_prog['slice_color'].write(np.array([1.0, 1.0, 1.0, 0.1], dtype='f4'))

        # bruh this polygon offset thing doesn't even work??
        ctx.polygon_offset = -0.2, -0.25
        ctx.disable(moderngl.CULL_FACE)
        ctx.disable(moderngl.DEPTH_TEST)
        ctx.depth_mask = False

        plane_vao.render(moderngl.TRIANGLES)

        ctx.polygon_offset = 0, 0

        #translation
        model = glm.translate(model, model_pos)
        #rotation
        model = model * glm.mat4_cast(model_ori) # Apply the quaternion rotation
        #scaling
        model = glm.scale(model, glm.vec3(zoom, zoom, zoom))

        current_transformed_tris = transform_triangles(np.array(current_transformed_tris, dtype='f4'), model)
        slice_plane_eq = get_slice_plane_eq()

        prog['model'].write(np.array(model.to_list(), dtype='f4'))
        prog['slice_plane'].write(np.array(slice_plane_eq.to_list(), dtype='f4'))

        ctx.enable(moderngl.CULL_FACE)
        ctx.enable(moderngl.DEPTH_TEST)
        ctx.depth_mask = True

        vao.render(moderngl.TRIANGLES)

        if redraw:
            print(f"A: {get_slice_plane_eq().x}, B: {get_slice_plane_eq().y}, C: {get_slice_plane_eq().z}, D:{get_slice_plane_eq().w}")
            print(get_slice_plane_eq())

            print(current_transformed_tris[0, 0])
            print(f"model_pos:{model_pos}")

            test_prog = ctx.program(vertex_shader="""
                #version 330 core
                                    
                in vec3 vert_pos;
                in float outline_thickness;
                
                uniform mat4 model, view, projection;
                
                void main(){
                    gl_Position = projection * view * model * vec4(vert_pos, 1.0);
                }
            """,
            fragment_shader="""
                #version 330 core

                out vec4 outColor;

                void main(){
                    outColor = vec4(1.0, 0.0, 0.0, 1.0);
                }
            """)

            test_vbo = ctx.buffer(current_transformed_tris.tobytes())
            test_vao = ctx.vertex_array(
                test_prog,
                [
                    (test_vbo, '3f', 'vert_pos')
                ]
            )
            
            test_prog['model'].write(np.array(glm.mat4(1.0).to_list(), dtype='f4'))
            test_prog['view'].write(np.array(view.to_list(), dtype='f4'))
            test_prog['projection'].write(np.array(projection.to_list(), dtype='f4'))

            test_vao.render(moderngl.TRIANGLES)


        # print(f"A: {get_slice_plane_eq().x}, B: {get_slice_plane_eq().y}, C: {get_slice_plane_eq().z}, D:{get_slice_plane_eq().w}")

        if cross_section and redraw:
            img = make_img_np(get_slice_plane_eq(), current_transformed_tris, width=1024, height=1024)
            cv.imshow("Cross Section", img)
            cv.waitKey(1)
            redraw = False

        prev_mouse_x = mouse_x
        prev_mouse_y = mouse_y

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    render(path="Files/test_cone.stl", cross_section=False)
    path = "Files/test_cone.stl"