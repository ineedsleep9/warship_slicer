import glfw
import numpy as np

from OpenGL.GL import *
import OpenGL.GL.shaders

def main():
    if not glfw.init():
        return

    window = glfw.create_window(1200, 800, "ModernGL", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glClearColor(0, 0, 0, 0)

    #       POSITIONS      COLOURS
    quad = [-0.5, -0.5, 0,  1, 0, 0,
            0.5, -0.5, 0,   0, 1, 0,
            0.5, 0.5, 0,    0, 0, 1,
            -0.5, 0.5, 0,   1, 1, 1]

    quad = np.array(quad, dtype=np.float32)

    indices = [0, 1, 2,
                2, 3, 0]

    indices = np.array(indices, dtype=np.uint32)

    vertex_shader = """
    #version 330
    in vec3 position;
    in vec3 color;

    out vec3 newColor;
    void main(){
        gl_Position = vec4(position, 1.0f);
        newColor = color;
    }
    """

    fragment_shader = """
    #version 330
    in vec3 newColor;
    out vec4 outColor;
    void main(){
        outColor = vec4(newColor, 1.0f);
    }
    """

    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                                            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    #tri has 9 float values, each of which take up 4 bytes => 9 * 4 = 36
    #review GL_STATIC_DRAW, GL_DYNAMIC_DRAW, GL_STREAM_DRAW
    glBufferData(GL_ARRAY_BUFFER, 96, quad, GL_STATIC_DRAW)
    
    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, 24, indices, GL_STATIC_DRAW)

    position = glGetAttribLocation(shader, "position")
    # index, size, type (float), normalized (false), stride (offset, skip 24 bytes to get to position again), starting pointer (points to pos. of first wanted value)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)

    color = glGetAttribLocation(shader, "color")
    # index, size, type (float), normalized (false), stride (offset, skip 24 bytes to get to position again), starting pointer (points to pos. of first wanted value)
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)

    glUseProgram(shader)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()