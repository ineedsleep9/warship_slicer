import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

from extract_file import get_normals, get_vectors

def shift_center(vectors):
    min_p = np.min(vectors, axis=0)
    max_p = np.max(vectors, axis=0)

    center = (min_p + max_p)/2

    return vectors - center

def display_stl(path="Files/test_cone.stl", window_size=(1200, 800)):
    vectors = get_vectors(path)

    pygame.init()

    FPS = 60
    clock = pygame.time.Clock()

    display = pygame.display.set_mode(window_size, DOUBLEBUF|OPENGL, 24)

    gluPerspective(45, 1, 1, 500)
    glClearColor(0.0, 0.0, 0.0, 0.0)

    glTranslatef(0.0, 0.0, -400)
    glScalef(3.5, 3.5, 3.5)

    # vectors = shift_center(vectors)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #left click
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[2]:
                    glRotatef(event.rel[0], 0, 1, 0)
                    glRotatef(event.rel[1], 1, 0, 0)

            #Mouse Wheel
            if event.type == pygame.MOUSEWHEEL:
                # mouse_x, mouse_y = event.pos
                scale = event.y/10 + 1
                glScalef(scale, scale, scale)

            #right click
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[2]:
                    print(event.rel)
        
        glClear(GL_COLOR_BUFFER_BIT)
        # glRotatef(5, 1, 0, 0)
        # glTranslatef(0, 0, 0)
        # glScalef(1.01, 1.01, 1.01)

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
    display_stl()