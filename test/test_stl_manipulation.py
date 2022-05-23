from am_stl.stl.stl_parser import STLfile
import numpy as np


def test_rotate_geometry():
    error_tolerance = 0.001
    stl_file_1 = STLfile(r"test/test_assets/bin-test-cube-0.stl")
    facecol = stl_file_1.load(print_time_info=False, strict_vertex_policy=False, ignore_edges=True)
    bad_faces, ok_faces = facecol.check_for_problems(ignore_grounded=True, ground_level=stl_file_1.ground_level)
    affected_area = facecol.affected_area

    assert len(bad_faces) == 2
    assert len(ok_faces) == 10
    assert abs(facecol.affected_area - 10000) < error_tolerance
    assert abs(facecol.affected_area - facecol.affected_area_projected) < error_tolerance

    for axis in ["x", "y"]:
        for angle_in_deg in [10, 20, 30, 40]:
            theta = (2*np.pi / 360) * angle_in_deg
            stl_file_1.rotate(theta, axis)
            bad_faces, ok_faces = facecol.check_for_problems(ignore_grounded=True, ground_level=stl_file_1.ground_level)

            assert len(bad_faces) == 2
            assert len(ok_faces) == 10
            assert abs(facecol.affected_area - 10000) < error_tolerance
            assert abs(facecol.affected_area_projected - facecol.affected_area*np.cos(theta)) < error_tolerance

            stl_file_1.rotate(-theta, axis)
