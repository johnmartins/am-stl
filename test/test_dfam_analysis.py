from am_stl.stl.stl_parser import STLfile


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


def test_ascii_get_affected_area():
    pass


def test_bin_get_affected_area():
    pass
