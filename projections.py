import numpy as np
import glm

def project_point_to_plane(point, origin, u, v):
    # Ensure all are GLM vectors
    point = glm.vec3(*point) if isinstance(point, tuple) else point
    origin = glm.vec3(*origin) if isinstance(origin, tuple) else origin
    u = glm.vec3(*u) if isinstance(u, tuple) else u
    v = glm.vec3(*v) if isinstance(v, tuple) else v

    pos_vec = point - origin
    x = glm.dot(pos_vec, u)
    y = glm.dot(pos_vec, v)
    return (x, y)


def project_segments_to_2d(segments, plane_eq):
    plane_normal = glm.vec3(plane_eq.x, plane_eq.y, plane_eq.z)

    # Calculate a point on the plane: choose any point such that Ax + By + Cz + D = 0
    # We'll use a point along the normal direction at distance -D/|N|^2
    normal_len_squared = glm.dot(plane_normal, plane_normal)
    if normal_len_squared == 0:
        raise ValueError("Invalid plane normal: zero vector")
    t = -plane_eq.w / normal_len_squared
    plane_pos = plane_normal * t

    # Generate orthonormal basis
    u = glm.normalize(glm.cross(plane_normal, glm.vec3(0, 0, 1)))
    if glm.length(u) < 0.01:
        u = glm.normalize(glm.cross(plane_normal, glm.vec3(0, 1, 0)))
    v = glm.normalize(glm.cross(plane_normal, u))

    projected_pts = []
    for p1, p2 in segments:
        projected_pts.append((project_point_to_plane(p1, plane_pos, u, v), project_point_to_plane(p2, plane_pos, u, v)))

    return projected_pts, plane_pos, u, v

def unproject_2d_to_3d(pts_2d, plane_pos, u, v):
    return [plane_pos + pt[0]*u + pt[1]*v for pt in pts_2d]