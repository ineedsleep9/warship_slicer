import numpy as np
import glm

def project_point_to_plane(point, origin, u_axis, v_axis):
    pos_vec = point - origin
    return np.array([glm.dot(pos_vec, u_axis), glm.dot(pos_vec, v_axis)])

def project_segments_to_2d(segments, plane_pos, plane_normal):
    # Generate orthonormal basis
    u = glm.normalize(glm.cross(plane_normal, glm.vec3(0, 0, 1)))
    if glm.length(u) < 0.01:
        u = glm.normalize(glm.cross(plane_normal, glm.vec3(0, 1, 0)))
    v = glm.normalize(glm.cross(plane_normal, u))

    projected_pts = []
    for p1, p2 in segments:
        projected_pts.append(project_point_to_plane(p1, plane_pos, u, v))
        projected_pts.append(project_point_to_plane(p2, plane_pos, u, v))
    return projected_pts, u, v

def unproject_2d_to_3d(pts_2d, plane_pos, u, v):
    return [plane_pos + pt[0]*u + pt[1]*v for pt in pts_2d]