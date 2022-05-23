from am_stl.stl.stl_parser import STLfile
from am_stl.stl.stl_builder import STLCreator
import tempfile
import uuid


def test_load_ascii():
    stl_file = STLfile(r"test/test_assets/ascii_test_model.stl")
    face_collection = stl_file.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)

    assert len(stl_file.vertices) == 5106
    assert len(stl_file.normals) == 5106/3
    assert len(face_collection.faces) == 5106/3
    assert stl_file.header == "solid GeoAlt\n"


def test_load_binary():
    stl_file = STLfile(r"test/test_assets/bin_test_model.stl")
    face_collection = stl_file.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)

    assert len(stl_file.vertices) == 20580
    assert len(stl_file.normals) == 20580/3
    assert len(face_collection.faces) == 20580/3


def test_save_ascii():
    stl_file_1 = STLfile(r"test/test_assets/bin_test_model.stl")
    face_collection_1 = stl_file_1.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)

    vertices_count = len(stl_file_1.vertices)
    normals_count = len(stl_file_1.normals)
    faces_count = len(face_collection_1.faces)

    tmp_file_name = f'{tempfile.tempdir}/{uuid.uuid4()}.stl'
    stl_creator = STLCreator(tmp_file_name, face_collection_1)
    stl_creator.build_file()

    stl_file_2 = STLfile(tmp_file_name)
    face_collection_2 = stl_file_2.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)

    assert len(stl_file_2.vertices) == vertices_count
    assert len(stl_file_2.normals) == normals_count
    assert len(face_collection_2.faces) == faces_count
