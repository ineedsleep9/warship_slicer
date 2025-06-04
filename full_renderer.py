import glfw
import numpy as np
import glm
import moderngl

from extract_file import get_vectors, get_vertex_attributes


def main():
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

    tri = get_vertex_attributes(path="Files/enterprise.stl")
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
            outColor = vec4((1.0f, 1.0f, 1.0f) - normal_out * 0.9, 1.0f);
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

    print(len(get_vectors(path="Files/enterprise.stl")))
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

    tri = get_vertex_attributes(path="Files/enterprise.stl")
    print("Loaded triangles:", len(tri), "Floats:", tri[:10])

    tri = np.array(tri, dtype='f4')
    print("tri.shape:", tri.shape)

    t = 0.0
    while not glfw.window_should_close(window):
        t += 0.01 # put delta time her pls
        glfw.poll_events()

        ctx.clear(0.0, 0.0, 0.0, 1.0)

       # Euler angles in radians (pitch, yaw, roll)
        pitch = glm.radians(30.0)  # rotation around X
        yaw   = glm.radians(45.0)  # rotation around Y
        roll  = glm.radians(60.0)  # rotation around Z

        # Create rotation matrix from Euler angles
        rotation = glm.mat4(1.0)
        rotation = glm.rotate(rotation, pitch * t, glm.vec3(1, 0, 0))  # X-axis
        rotation = glm.rotate(rotation, yaw,   glm.vec3(0, 1, 0))  # Y-axis
        rotation = glm.rotate(rotation, roll,  glm.vec3(0, 0, 1))  # Z-axis

        # # Send transformation matrices
        # glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(rotation))
        # glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
        # glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))

        prog['model'].write(np.array(rotation.to_list(), dtype='f4'))

        vao.render(moderngl.TRIANGLES)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
