import numpy as np
from stl import mesh, Mode

def get_vectors(path="Files/test_cone.stl"):
    model = mesh.Mesh.from_file(path)

    vectors = model.vectors
    return vectors

def get_normals(path="Files/test_cone.stl"):
    model = mesh.Mesh.from_file(path)

    normals = model.normals
    return normals

def get_vertex_attributes(path="Files/test_cone.stl"):
    v = get_vectors(path)
    n = get_normals(path)

    ans = []

    for i in range(len(v)):
        for j in range(3):
            pos = v[i][j]    # (x, y, z)
            norm = n[i]    # (nx, ny, nz) same for all 3 verts in triangle
            ans.append(np.concatenate([pos, norm]))
    
    return ans

if __name__ == "__main__":
    print(get_vectors())
    print(get_normals())