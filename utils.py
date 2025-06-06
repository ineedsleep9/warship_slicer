import glm

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