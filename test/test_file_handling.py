from am_stl.stl.stl_parser import STLfile
from am_stl.stl.stl_builder import STLCreator
from timeit import default_timer as timer
import numpy as np
import tempfile
import uuid


def test_load_ascii():
    stl_file = STLfile(r"test/test_assets/ascii_test_model.stl")
    face_collection = stl_file.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=True)

    assert len(bad_faces) == 580
    assert len(ok_faces) == 1122


def test_load_binary():
    stl_file = STLfile(r"test/test_assets/bin_test_model.stl")
    face_collection = stl_file.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=True)

    assert len(bad_faces) == 664
    assert len(ok_faces) == 6196


def test_save_ascii():
    stl_file_1 = STLfile(r"test/test_assets/bin_test_model.stl")
    face_collection_1 = stl_file_1.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)
    bad_faces_1, ok_faces_1 = face_collection_1.check_for_problems(ignore_grounded=True)

    bad_face_count = len(bad_faces_1)
    ok_face_count = len(ok_faces_1)

    tmp_file_name = f'{tempfile.tempdir}/{uuid.uuid4()}.stl'
    stl_creator = STLCreator(tmp_file_name, face_collection_1)
    stl_creator.build_file()

    stl_file_2 = STLfile(tmp_file_name)
    face_collection_2 = stl_file_2.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)
    bad_faces_2, ok_faces_2 = face_collection_2.check_for_problems(ignore_grounded=True)

    assert bad_face_count == len(bad_faces_2)
    assert ok_face_count == len(ok_faces_2)
