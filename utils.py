import glm
import numpy as np

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

def transform_triangles(triangles, model_matrix):
    if triangles.shape[1] == 6:
        positions = triangles[:, :3]
    else:
        positions = triangles.reshape(-1, 3, 3)

    positions_h = np.concatenate([
        positions.reshape(-1, 3),
        np.ones((positions.shape[0] * 3, 1), dtype=positions.dtype)
    ], axis=1)

    # Convert glm.mat4 to NumPy array
    model_np = np.array(model_matrix.to_list(), dtype=np.float32).reshape(4, 4)

    transformed_positions_h = (model_np @ positions_h.T).T
    transformed_positions = transformed_positions_h[:, :3]
    transformed_triangles = transformed_positions.reshape(-1, 3, 3)

    return transformed_triangles


def transform_triangles_with_normals(triangles, model_matrix):
    # triangles: (N, 6) = [x, y, z, nx, ny, nz]

    # Transform positions with full 4x4 matrix
    positions = np.hstack([triangles[:, :3], np.ones((triangles.shape[0], 1), dtype=np.float32)])  # (N,4)
    transformed_positions = (model_matrix @ positions.T).T[:, :3]

    # Transform normals with normal matrix (inverse transpose of upper 3x3)
    normal_matrix = np.linalg.inv(model_matrix[:3, :3]).T
    transformed_normals = (normal_matrix @ triangles[:, 3:].T).T

    # Normalize normals (important after transformation)
    norm_lengths = np.linalg.norm(transformed_normals, axis=1, keepdims=True)
    transformed_normals /= norm_lengths + 1e-8

    return np.hstack([transformed_positions, transformed_normals])