import glfw
import moderngl
import numpy as np
from pyrr import Matrix44

from OpenGL.GL import *

def main():
    if not glfw.init():
        raise Exception("GLFW can't be initialized")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    window = glfw.create_window(1200, 800, "ModernGL", None, None)

    if not window:
        glfw.terminate()
        raise Exception("GLFW window creation failed")

    glfw.make_context_current(window)

    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND)

    glClearColor(0, 0, 0, 0)

    #       POSITIONS      COLOURS
    tri = [-0.5, -0.5, 0,  1, 0, 0,
           0.5, -0.5, 0,   0, 1, 0,
           0.5, 0.5, 0,    0, 0, 1]

    tri = np.array(tri, dtype=np.float32)

    prog = ctx.program(vertex_shader = """
        #version 330
        in vec3 position;
        in vec3 color;
        out vec3 newColor;
        
        void main(){
            gl_Position = vec4(position, 1.0);
            newColor = color;
        }
        """,
        fragment_shader = """
        #version 330
        in vec3 newColor;
        out vec4 outColor;
        void main(){
            outColor = vec4(newColor, 1.0);
        }
        """
    )

    vbo = ctx.buffer(tri.tobytes())
    vao = ctx.vertex_array(
        prog,
        [
            (vbo, '3f 3f', 'position', 'color'),
        ]
    )

    while not glfw.window_should_close(window):
        glfw.poll_events()

        ctx.clear(0, 0, 0, 0)
        vao.render(moderngl.TRIANGLES)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()