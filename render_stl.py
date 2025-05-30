import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from stl import mesh
from extract_file import get_normals, get_vectors

def render(path="Files//test_cone.stl"):
    vectors = get_vectors(path)

    pygame.init()

    FPS = 60
    clock = pygame.time.Clock()

    display = pygame.display.set_mode((1200, 800), DOUBLEBUF|OPENGL, 24)

    gluPerspective(45, 1, 1, 500)
    glClearColor(0.0, 0.0, 0.0, 0.0)

    glTranslatef(0.0, 0.0, -400)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        glClear(GL_COLOR_BUFFER_BIT)
        glRotatef(1, 1, 0, 0)

        #Draw filled triangles
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        #GL_TRIANGLES because we are drawing triangles
        glBegin(GL_TRIANGLES)

        #specify triangle color
        glColor3f(0.0, 0.0, 0.0)

        for tri in vectors:
            for vertex in tri:
                glVertex3fv(vertex)

        glEnd()
        
        #Draw outlines
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(2)

        #GL_TRIANGLES because we are drawing triangles
        glBegin(GL_TRIANGLES)

        #specify triangle color
        glColor3f(1.0, 1.0, 1.0)

        for tri in vectors:
            for vertex in tri:
                glVertex3fv(vertex)

        glEnd()

        pygame.display.flip()
        pygame.display.set_caption(str(clock.get_fps()))
        clock.tick(FPS)

if __name__ == "__main__":
    print(get_vectors())
    print(get_normals())

    # triangles=[
    #         ((-1.0, -1.0, -5.0), (1.0, -1.0, -5.0), (0.0, 1.0, -5.0)),
    #         ((-1, -1, -5), (-1, 1, -5), (0, 1, -5)),
    #         ((1, -1, -5), (1, 1, -5), (0, 1, -5))
    #     ]

    render()