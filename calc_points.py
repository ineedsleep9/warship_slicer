import glm
import cv2 as cv
import numpy as np
# from make_loops import make_loops
from extract_file import get_vectors, get_normals
from projections import project_point_to_plane, project_segments_to_2d, unproject_2d_to_3d, is_nan_point

#rounds points to dp decimal places
def round_pt(pt, dp=6):
    return tuple(round(coord, dp) for coord in pt)

def get_intersection_segments(tris, plane_eq):
    EPSILON = 1e-8
    ans = []

    for tri in tris:
        dists = [glm.dot(plane_eq, glm.vec4(*v, 1.0)) for v in tri]
        intersection_points = []

        if all(abs(d) <= EPSILON for d in dists):
            a, b, c = tri[0], tri[1], tri[2]
            ans.append((a, b))
            ans.append((b, c))
            ans.append((c, a))
            continue

        for i in range(3):
            v1, d1 = tri[i], dists[i]
            v2, d2 = tri[(i + 1) % 3], dists[(i + 1) % 3]
            p1, p2 = glm.vec3(*v1), glm.vec3(*v2)

            # Case: vertex lies on the plane
            if abs(d1) <= EPSILON:
                if p1 not in intersection_points:
                    intersection_points.append(p1)

            # Case: edge crosses the plane
            if d1 * d2 < -EPSILON:
                denom = d1 - d2
                if abs(denom) < EPSILON:
                    continue  # skip this degenerate case
                t = d1 / denom
                intersection_points.append(p1 + t * (p2 - p1))

        if len(intersection_points) == 2:
            ans.append((intersection_points[0], intersection_points[1]))

    return ans


def make_img_np(plane_eq, tris, width = 1024, height = 1024, aspect_ratio=-1):
    intersect_segs = get_intersection_segments(tris, plane_eq)
    intersect_segs, plane_pos, u, v = project_segments_to_2d(intersect_segs, plane_eq)

    if len(intersect_segs) == 0:
        print("NO INTERSECTIONS")
        return np.ones((width, height), dtype=np.uint8)

    all_pts = np.array([pt for seg in intersect_segs for pt in seg])

    min_uv = np.min(all_pts, axis=0)
    max_uv = np.max(all_pts, axis=0)

    x_offset = 20
    y_offset = 20

    xy_img = max_uv - min_uv
    if aspect_ratio == -1:
        multiple = min((width - 2 * x_offset) / xy_img[0], (height - 2 * y_offset) / xy_img[1])
    x_offset += (width - 2 * x_offset - multiple * xy_img[0])/2
    y_offset += (height - 2 * y_offset - multiple * xy_img[1])/2

    print(f"min_uv: {min_uv}, max_uv: {max_uv}")
    print(f"Bounding box size: {xy_img}")

    def uv_to_pixel(uv):
        if is_nan_point(uv):
            raise ValueError(f"NaN in UV: {uv}")
        x = (uv[0] - min_uv[0]) * multiple + x_offset
        y = (max_uv[1] - uv[1]) * multiple + y_offset

        x = max(0, min(width - x_offset - 1, x))
        y = max(0, min(height - y_offset - 1, y))
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
        cv.line(img, (int(p1[0]), int(p1[1])),
             (int(p2[0]), int(p2[1])),
             color=0, thickness=1)
        cnt += 1

        # print(f"Segment {cnt}: {p1} -> {p2}")


    print("number of segments printed: " + str(cnt))

    return img