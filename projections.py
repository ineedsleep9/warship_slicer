import numpy as np
import glm
import math

def is_nan_point(pt):
    return any(math.isnan(coord) for coord in pt)

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

def build_projection_basis(plane_eq):
    """Build orthonormal basis (u, v) from plane normal"""
    normal = glm.vec3(plane_eq.x, plane_eq.y, plane_eq.z)

    if glm.length(normal) == 0:
        raise ValueError("Plane normal is zero vector")

    normal = glm.normalize(normal)

    # Choose an up vector that's not parallel to the normal
    up = glm.vec3(0, 0, 1)
    if abs(glm.dot(up, normal)) > 0.999:
        up = glm.vec3(0, 1, 0)  # switch if parallel

    u = glm.normalize(glm.cross(up, normal))
    v = glm.normalize(glm.cross(normal, u))

    return u, v


def project_segments_to_2d(segments, plane_eq):
    plane_normal = glm.vec3(plane_eq.x, plane_eq.y, plane_eq.z)

    # Calculate a point on the plane: choose any point such that Ax + By + Cz + D = 0
    # We'll use a point along the normal direction at distance -D/|N|^2
    normal_len_squared = glm.dot(plane_normal, plane_normal)
    if normal_len_squared == 0:
        raise ValueError("Invalid plane normal: zero vector")
    t = -plane_eq.w / normal_len_squared
    plane_pos = plane_normal * t

    u,v = build_projection_basis(plane_eq)

    projected_pts = []
    for p1, p2 in segments:
        proj1 = project_point_to_plane(p1, plane_pos, u, v)
        proj2 = project_point_to_plane(p2, plane_pos, u, v)

        if is_nan_point(proj1) or is_nan_point(proj2):
            print(f"NaN detected: p1={p1}, p2={p2}, plane_pos={plane_pos}, u={u}, v={v}")
        else:
            projected_pts.append((proj1, proj2))


    return projected_pts, plane_pos, u, v

def unproject_2d_to_3d(pts_2d, plane_pos, u, v):
    return [plane_pos + pt[0]*u + pt[1]*v for pt in pts_2d]