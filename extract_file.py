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

if __name__ == "__main__":
    print(get_vectors())
    print(get_normals())