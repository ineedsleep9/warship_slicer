import glm
import numpy as np
# from make_loops import make_loops
from extract_file import get_vectors, get_normals

#rounds points to dp decimal places
def round_pt(pt, dp=6):
    return tuple(round(coord, dp) for coord in pt)

#returns list of lists
def get_intersection_segments_normals(path, plane_eq):
    EPSILON = 1e-7
    tris = get_vectors(path=path)
    norms = get_vectors(path=path)

    ans = []
    for tri in tris:
        dists = []
        n = norms[0]
        norms = norms[1:]

        for v in tri:
            dists.append(glm.dot(plane_eq, glm.vec4(*v, 1.0)))
        
        if abs(dists[0]) <= EPSILON and abs(dists[1]) <= EPSILON and abs(dists[2]) <= EPSILON:
            a, b, c = round_pt(tri[0]), round_pt(tri[1]), round_pt(tri[2])
            ans.append((a, b, n))
            ans.append((b, c, n))
            ans.append((c, a, n))
            continue

        intersection_points = []
        
        for i in range(3):
            v, d = tri[i], dists[i]
            p = glm.vec3(*v)

            j = (i + 1)%3
            v2, d2 = tri[j], dists[j]
            p2 = glm.vec3(*v2)

            if abs(d) <= EPSILON and round_pt(p) not in intersection_points:
                intersection_points.append(round_pt(p))
            
            if d * d2 < -EPSILON:
                line = p2 - p

                num = d
                denom = d - d2
                t = -num/denom
                
                intersection_points.append(round_pt((p + t * line)))

        if len(intersection_points) >= 2:
            ans.append((intersection_points[0], intersection_points[1], n))

    return ans

