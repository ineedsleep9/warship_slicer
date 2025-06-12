import glm
import cv2 as cv
import numpy as np
import math
# from make_loops import make_loops
from extract_file import get_vectors, get_normals
from projections import project_point_to_plane, project_segments_to_2d, unproject_2d_to_3d

#rounds points to dp decimal places
def round_pt(pt, dp=6):
    return tuple(round(coord, dp) for coord in pt)

def is_nan_point(pt):
    return any(math.isnan(coord) for coord in pt)

def get_intersection_segments_normals(path, plane_eq):
    EPSILON = 1e-7
    tris = get_vectors(path=path)
    ans = []

    for tri in tris:
        dists = [glm.dot(plane_eq, glm.vec4(*v, 1.0)) for v in tri]
        intersection_points = []

        for i in range(3):
            v1, d1 = tri[i], dists[i]
            v2, d2 = tri[(i + 1) % 3], dists[(i + 1) % 3]
            p1, p2 = glm.vec3(*v1), glm.vec3(*v2)

            # Case: vertex lies on the plane
            if abs(d1) <= EPSILON:
                pt = round_pt(p1)
                if pt not in intersection_points:
                    intersection_points.append(pt)

            # Case: edge crosses the plane
            if d1 * d2 < -EPSILON:
                denom = d1 - d2
                if abs(denom) < EPSILON:
                    continue  # skip this degenerate case
                t = -d1 / denom
                intersection_points.append(round_pt(p1 + t * (p2 - p1)))

        # Optional: Handle triangle fully on the plane
        if all(abs(d) <= EPSILON for d in dists):
            a, b, c = round_pt(tri[0]), round_pt(tri[1]), round_pt(tri[2])
            ans.append((a, b))
            ans.append((b, c))
            ans.append((c, a))
        elif len(intersection_points) == 2:
            ans.append((intersection_points[0], intersection_points[1]))

    return ans


def make_img_np(plane_eq, path, width = 1024, height = 1024):
    intersect_segs = get_intersection_segments_normals(path, plane_eq)
    intersect_segs, plane_pos, u, v = project_segments_to_2d(intersect_segs, plane_eq)

    if len(intersect_segs) == 0:
        print("NO INTERSECTIONS")
        return

    all_pts = np.array([pt for seg in intersect_segs for pt in seg])

    min_uv = np.min(all_pts, axis=0)
    max_uv = np.max(all_pts, axis=0)

    print(f"min_uv: {min_uv}, max_uv: {max_uv}")
    print(f"Bounding box size: {max_uv - min_uv}")


    xy_img = max_uv - min_uv

    def uv_to_pixel(uv):
        if is_nan_point(uv):
            raise ValueError(f"NaN in UV: {uv}")
        x = int((uv[0] - min_uv[0]))
        y = int((max_uv[1] - uv[1]))  # flip Y for image coordinates

        # Clamp to image bounds
        x = max(0, min(width - 1, x))
        y = max(0, min(height - 1, y))
        return (x, y)



    img = np.ones((width, height), dtype = np.uint8)
    img *= 255

    print("Number of segments:" + str(len(intersect_segs)))

    cnt = 0

    for seg in intersect_segs:
        if is_nan_point(seg[0]) or is_nan_point(seg[1]):
            continue
        p1, p2 = seg
        p1 = uv_to_pixel(p1)
        p2 = uv_to_pixel(p2)
        cv.line(img, p1, p2, color=0, width=1)
        cnt += 1

        print(f"Segment {cnt}: {p1} -> {p2}")


    print("number of segments printed: " + str(cnt))

    cv.imshow("Cross Section", img)
    cv.waitKey()