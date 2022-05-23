from am_stl.stl.stl_parser import STLfile
import numpy as np


def test_ascii_problem_surface_identification():
    stl_file = STLfile(r"test/test_assets/ascii_test_model.stl")
    face_collection = stl_file.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=True)

    assert len(bad_faces) == 580
    assert len(ok_faces) == 1122
    assert len(bad_faces) + len(ok_faces) == len(face_collection.faces)


def test_bin_problem_surface_identification():
    stl_file = STLfile(r"test/test_assets/bin_test_model.stl")
    face_collection = stl_file.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=True)

    assert len(bad_faces) == 664
    assert len(ok_faces) == 6196
    assert len(bad_faces) + len(ok_faces) == len(face_collection.faces)


def test_get_affected_area_ignore_ground_01():
    error_tolerance = 0.001
    stl_file = STLfile(r"test/test_assets/bin-test-cube-0.stl")
    face_collection = stl_file.load(strict_vertex_policy=False, ignore_edges=True)

    # Expect two faces (one cube side) to be affected.
    # One edge = 100mm, one side thus has a total area of 10000mm^2
    # Affected area and projected affected area should be the same for this model.
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=True)

    assert len(bad_faces) == 2
    assert len(ok_faces) == 10
    assert abs(face_collection.affected_area - face_collection.affected_area_projected) < error_tolerance
    assert abs(face_collection.affected_area - 10000) < error_tolerance


def test_get_affected_area_with_ground_01():
    error_tolerance = 0.001
    stl_file = STLfile(r"test/test_assets/bin-test-cube-0.stl")
    face_collection = stl_file.load(strict_vertex_policy=False, ignore_edges=True)

    # Expect no faces to be affected, as the cube is placed on the ground.
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=False, ground_level=stl_file.ground_level)

    assert len(bad_faces) == 0
    assert len(ok_faces) == 12
    assert abs(face_collection.affected_area - face_collection.affected_area_projected) < error_tolerance
    assert abs(face_collection.affected_area) < error_tolerance


def test_get_affected_area_ignore_ground_02():
    error_tolerance = 0.001
    stl_file = STLfile(r"test/test_assets/bin-test-cube-40.stl")
    face_collection = stl_file.load(strict_vertex_policy=False, ignore_edges=True)

    # Expect two faces (one cube side) to be affected.
    # One edge = 100mm, one side thus has a total area of 10000mm^2
    # Affected area and projected affected area should be the same for this model.
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=True)

    assert len(bad_faces) == 2
    assert len(ok_faces) == 10
    # Affected area and projected area should not be the same, in this case.
    assert abs(face_collection.affected_area * np.cos(np.pi * 2 / 9) - face_collection.affected_area_projected) < error_tolerance
    assert abs(face_collection.affected_area - 10000) < error_tolerance


def test_get_affected_area_with_ground_02():
    error_tolerance = 0.001
    stl_file = STLfile(r"test/test_assets/bin-test-cube-40.stl")
    face_collection = stl_file.load(strict_vertex_policy=False, ignore_edges=True)

    # Expect two faces (one cube side) to be affected.
    # One edge = 100mm, one side thus has a total area of 10000mm^2
    # Affected area and projected affected area should be the same for this model.
    bad_faces, ok_faces = face_collection.check_for_problems(ignore_grounded=False, ground_level=stl_file.ground_level)

    assert len(bad_faces) == 2
    assert len(ok_faces) == 10
    # Affected area and projected area should not be the same, in this case.
    assert abs(face_collection.affected_area * np.cos(np.pi * 2 / 9) - face_collection.affected_area_projected) < error_tolerance
    assert abs(face_collection.affected_area - 10000) < error_tolerance
