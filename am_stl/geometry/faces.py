from typing import Tuple, List

import numpy as np

from am_stl.geometry.vertices import VertexCollection
from am_stl.geometry.edges import Edge, EdgeCollection


class FaceCollection:
    """
    Collection of Face objects
    """

    def __init__(self, stlfile):
        self.stlfile = stlfile
        self.faces = []
        self.problem_faces = []
        self.good_faces = []

        self.vertex_collection = VertexCollection()
        self.edge_collection = EdgeCollection()

        self.iterator_pointer = 0
        self.affected_area = 0                  # Total area of model that will interface with support structures
        self.affected_area_projected = 0        # Total area of substrate that will interface with support structures

    def append(self, face, ignore_edges=False):
        """
        Add face to face collection
        """

        if (isinstance(face, Face) is False):
            raise TypeError('face argument needs to be of type Face()')
        if face.has_bad_angle is True:
            self.problem_faces.append(face)
        else:
            self.good_faces.append(face)

        # This is where it is ensured using OOP that there only exists one instance of each unique vertex
        face.vertices[0] = self.vertex_collection.add(face.vertices[0])
        face.vertices[1] = self.vertex_collection.add(face.vertices[1])
        face.vertices[2] = self.vertex_collection.add(face.vertices[2])

        # Each unique vertex is marked as adjacent to the other vertices in the face.
        face.vertices[0].set_adjacency(face.vertices[1])
        face.vertices[0].set_adjacency(face.vertices[2])
        face.vertices[1].set_adjacency(face.vertices[2])

        self.faces.append(face)

        if ignore_edges is not True:
            face.set_edges(self.edge_collection)

        return

    def __iter__(self):
        """
        Contributes to making this class iterable by providing an interface
        """
        return self

    def __next__(self):
        """
        Contributes to making this class iterable by providing a pointer.
        """
        if self.iterator_pointer > (len(self.faces) - 1):
            self.iterator_pointer = 0
            raise StopIteration
        else:
            self.iterator_pointer += 1
            return self.faces[self.iterator_pointer - 1]

    def get_warning_count(self):
        """
        Returns the amount of potentially problematic faces
        """
        return len(self.problem_faces)

    def get_vertices(self, vtype="all"):
        return_array = []
        if vtype == "all":
            for f in self.faces:
                return_array.append(f.get_vertices_as_arrays())
        elif vtype == "bad":
            for f in self.problem_faces:
                return_array.append(f.get_vertices_as_arrays())
        elif vtype == "good":
            for f in self.good_faces:
                return_array.append(f.get_vertices_as_arrays())
        return return_array

    def get_vertex_collection(self):
        return self.vertex_collection

    def check_for_problems(self, phi_min=np.pi / 4, ignore_grounded=False, ground_level=0, ground_tolerance=0.01,
                           angle_tolerance=0.017) -> Tuple[List, List]:
        """
        Sets FaceCollection attributes FaceCollection.problem_faces and FaceCollection.good_faces.
        These attributes are lists, and are populated with the corresponding faces.
        :param phi_min: Tolerated angle
        :param ignore_grounded: Flat overhangs that are grounded are ignored.
        :param ground_level: Manually set the ground
        :param ground_tolerance: Tolerance for what counts as grounded or not
        :param angle_tolerance: Tolerance for acceptable overhang angles.
        :return: List of problem faces, List of good faces.
        """
        self.affected_area = 0
        self.affected_area_projected = 0
        self.good_faces = []
        self.problem_faces = []
        for f in self.faces:
            f.refresh_normal_vector()
            has_bad_angle = f.check_for_problems(phi_min=phi_min, ignore_grounded=ignore_grounded,
                                                 ground_level=ground_level, ground_tolerance=ground_tolerance,
                                                 angle_tolerance=angle_tolerance, no_weight_update=False)
            if has_bad_angle is True:
                self.problem_faces.append(f)
            else:
                self.good_faces.append(f)

        return self.problem_faces, self.good_faces


class Face:
    """
    STL polygon face
    """

    def __init__(self, face_collection, normal_index, vertex_index):
        """
        vert1, vert2, vert3: vertices of a polygon\n
        n: normal vector\n
        phi_min: minimum angular difference between normal vector and -z_hat before marked as a problematic surface
        """
        self.face_collection = face_collection
        self.normal_index = None
        self.vertex_index = None

        self.vertices = []

        self.affected_area = 0
        self.affected_area_projected = 0

        self.edge1 = None
        self.edge2 = None
        self.edge3 = None

        self.n = None  # The normal vector
        self.n_hat = None  # Normalized normal vector (unit vector)
        self.n_hat_original = None  # The original normalized normal vector from when the model was loaded the first time
        self.has_bad_angle = None  # True if this face has a problematic angle
        self.angle = None  # The angle compared to the xy-plane
        self.grounded = False
        self.vector1 = None
        self.vector2 = None

    def set_edges(self, edge_collection):
        # SLOW:
        self.edge1 = edge_collection.add(Edge(self.vertices[0], self.vertices[1]))
        self.edge2 = edge_collection.add(Edge(self.vertices[1], self.vertices[2]))
        self.edge3 = edge_collection.add(Edge(self.vertices[2], self.vertices[0]))

        # FAST:
        self.edge1.associate_with_face(self)
        self.edge2.associate_with_face(self)
        self.edge3.associate_with_face(self)

    def __connect_vertices__(self):
        """
        Connect all vertices to each other
        """
        self.vertices[0].set_adjacency(self.vertices[1])
        self.vertices[0].set_adjacency(self.vertices[2])
        self.vertices[1].set_adjacency(self.vertices[2])

    def get_top_z(self):
        z_array = np.array(self.get_vertices_as_arrays())[:, 2]
        return z_array[np.argsort(z_array)[2]]

    def refresh_normal_vector(self):
        self.vector1 = self.vertices[1].get_array() - self.vertices[0].get_array()
        self.vector2 = self.vertices[2].get_array() - self.vertices[0].get_array()
        self.n = np.cross(self.vector1, self.vector2)
        self.n_hat = self.n / np.linalg.norm(self.n)
        return self.n_hat

    def check_for_problems(self, phi_min=np.pi / 4, ignore_grounded=False, ground_level=0, ground_tolerance=0.01,
                           angle_tolerance=0.017, no_weight_update=True):
        """
        phi_min: Min angle before problem, in rads.\n

        ignore_grounded: Ignore surfaces close to the floor (prone to visual buggs in python)\n

        ground_level: The z-index of the ground\n

        ground_tolerance: How close a vertex needs to be to the ground in order to be considered as touching it.\n

        angle_tolerance: How close to the phi_min an angle needs to be in order to be considered as acceptable.
        Setting this to 0 causes the problem correction process to take much more time.\n
        """
        # Check the angle of the normal factor, and compare it to that of the inverted z-unit vector
        neg_z_hat = [0, 0, -1]
        angle = np.arccos(np.clip(np.dot(self.n_hat, neg_z_hat), -1.0, 1.0))
        self.angle = angle
        self.grounded = False
        return_value = None

        # Check if angle is within problem threshold
        if angle >= 0 and angle < phi_min:

            self.grounded = self.check_grounded(ground_level, ground_tolerance)
            if self.grounded is True and ignore_grounded is False:  # Check if grounded
                self.has_bad_angle = False
                return_value = False

            elif (angle - phi_min) ** 2 < angle_tolerance ** 2:  # Check if inside tolerence
                self.has_bad_angle = False
                return_value = False

            else:
                # If the angle is bad, and it is not on the ground, and is outside of tolerances, then mark it as a bad angle.
                self.has_bad_angle = True
                return_value = True

        else:
            # The angle is outside of the problem threshold and should thus be marked as an accepted angle.
            self.has_bad_angle = False
            return_value = False

        # Calculate weight
        self.calculate_affected_area(phi_min=phi_min, no_update=no_weight_update, ignore_grounded=ignore_grounded)

        return return_value

    def calculate_affected_area(self, phi_min=np.pi / 4, no_update=True, ignore_grounded=False):

        # Calculate face area
        cross_face = np.cross([self.vector1[0], self.vector1[1], self.vector1[2]],
                               [self.vector2[0], self.vector2[1], self.vector2[2]])
        area_face = np.linalg.norm(cross_face) / 2

        # Calculate area of projection onto XY plane
        cross_projection = np.cross([self.vector1[0], self.vector1[1], 0], [self.vector2[0], self.vector2[1], 0])
        area_projection = np.linalg.norm(cross_projection) / 2

        if self.grounded and ignore_grounded is False:
            # Does not add to total tally of affected area
            return 0

        if self.has_bad_angle is False:
            # Angle is problematic. Add to tally
            return 0

        if no_update is False:
            self.affected_area = area_face
            self.affected_area_projected = area_projection
            self.face_collection.affected_area += area_face
            self.face_collection.affected_area_projected += area_projection

        return self.affected_area, self.affected_area_projected

    def get_vertices_as_arrays(self):
        return np.array([self.vertices[0].get_array(), self.vertices[1].get_array(), self.vertices[2].get_array()])

    def get_vertices(self):
        return [self.vertices[0], self.vertices[1], self.vertices[2]]

    def get_edges(self):
        return [self.edge1, self.edge2, self.edge3]

    def __lt__(self, other):
        if self.get_top_z() > other.get_top_z():
            return True
        else:
            return False

    def check_grounded(self, ground_level, ground_tolerance):
        """
        Check if this surface is parallel to the ground.
        """
        # Calculate differences between individual vertex Z-elements, and the ground level.
        diff_1 = np.abs(self.vertices[0].get_array()[2] - ground_level)
        diff_2 = np.abs(self.vertices[1].get_array()[2] - ground_level)
        diff_3 = np.abs(self.vertices[2].get_array()[2] - ground_level)

        # If any of the ground levels is above the threshold, then return false, else return true.
        if diff_1 > ground_tolerance or diff_2 > ground_tolerance or diff_3 > ground_tolerance:
            return False

        return True

    def calculate_normal_vector(self):
        n = np.cross((self.vertices[1].get_array() - self.vertices[0].get_array()),
                     (self.vertices[2].get_array() - self.vertices[1].get_array()))
        return n / np.linalg.norm(n)

    def __eq__(self, other):
        if self.vertices[0] not in other.get_vertices():
            return False
        if self.vertices[1] not in other.get_vertices():
            return False
        if self.vertices[2] not in other.get_vertices():
            return False
        return True