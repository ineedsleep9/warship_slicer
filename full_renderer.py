import glfw
import numpy as np
import glm
import moderngl

from extract_file import get_vectors, get_vertex_attributes

#mouse events
prev_mouse_x = 0.0
prev_mouse_y = 0.0
start_trackball = glm.vec3(0.0, 0.0, 0.0)

left_click = False
right_click = False

mouse_scroll = 0.0
zoom = 1.0

model_pos = glm.vec3(0.0, 0.0, 0.0)
model_ori = glm.quat(1.0, 0.0, 0.0, 0.0)

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

def map_mouse_to_sphere(x, y, width, height):
    # Normalize mouse coordinates to [-1, 1] range relative to the window center
    nx = (2.0 * x / width) - 1.0
    ny = 1.0 - (2.0 * y / height) # Invert y for OpenGL's Y-up convention

    radius_sq = nx * nx + ny * ny
    z = 0.0

    if radius_sq <= 1.0: # Mouse is inside the circle projected onto the screen
        z = glm.sqrt(1.0 - radius_sq)
    else: # Mouse is outside the circle, project to the edge (equator)
        # Normalize the vector to the circle's edge
        length = glm.sqrt(radius_sq)
        nx /= length
        ny /= length
        z = 0.0 # On the equator

    return glm.vec3(nx, ny, z)

def render(path="Files/enterprise.stl"):
    global prev_mouse_x, prev_mouse_y, start_trackball
    global mouse_scroll, zoom
    global left_click, right_click
    global model_pos, model_ori

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

    ctx.clear(0.0, 0.0, 0.0, 1.0)

    #mouse event stuff
    glfw.set_mouse_button_callback(window, click_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    tri = get_vertex_attributes(path)
    tri = np.array(tri, dtype='f4')

    prog = ctx.program(vertex_shader = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec3 normal;
        out vec3 normal_out;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main() {
            gl_Position = projection * view * model * vec4(position, 1.0);
            normal_out = normal;
        }
        """,
        fragment_shader = """
        #version 330 core
        out vec4 outColor;
        in vec3 normal_out;

        void main() {
            outColor = vec4(0.5 + normal_out * 0.5, 1.0f);
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

    print(len(get_vectors(path)))
    print(tri.nbytes)

    # # Get uniform locations
    # model_loc = glGetUniformLocation(shader, "model")
    # view_loc = glGetUniformLocation(shader, "view")
    # proj_loc = glGetUniformLocation(shader, "projection")

    # Transformation Matrices
    model = glm.mat4(1.0)
    view = glm.lookAt(glm.vec3(20, 20, 20), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    projection = glm.perspective(glm.radians(45.0), 1200 / 800, 0.1, 100.0)

    prog['view'].write(np.array(view.to_list(), dtype='f4'))
    prog['projection'].write(np.array(projection.to_list(), dtype='f4'))

    tri = get_vertex_attributes(path)
    print("Loaded triangles:", len(tri), "Floats:", tri[:10])

    tri = np.array(tri, dtype='f4')
    print("tri.shape:", tri.shape)

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

            model_pos += dx * cam_right
            model_pos -= dy * cam_up

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

                # Accumulate the new rotation onto the existing model orientation
                # This order (new_quat * old_quat) applies rotations in world space.
                # For a "trackball" that orbits a central point, this usually feels natural.
                model_ori = rotation_quat * model_ori

                # Normalize the quaternion periodically to prevent floating-point drift
                model_ori = glm.normalize(model_ori)

            start_trackball = current_trackball

        model = glm.mat4(1.0)

        # scaling with mouse wheel
        if mouse_scroll != 0.0:
            scale = 1 + mouse_scroll / 50
            zoom *= scale
            if zoom < 0.001:
                zoom = 0.001
            mouse_scroll = 0

        #translation
        model = glm.translate(model, model_pos)
        
        #rotation
        model = model * glm.mat4_cast(model_ori) # Apply the quaternion rotation

        #scaling
        model = glm.scale(model, glm.vec3(zoom, zoom, zoom))

        # # Send transformation matrices
        # glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(rotation))
        # glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        # glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))

        prog['model'].write(np.array(model.to_list(), dtype='f4'))

        vao.render(moderngl.TRIANGLES)

        prev_mouse_x = mouse_x
        prev_mouse_y = mouse_y

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    render()
