from am_stl.exceptions import STL_LEAK_EXCEPTION
from am_stl.geometry.vertices import Vertex


class EdgeCollection(set):
    """
    Collection of Edge objects
    """
    def __init__(self):
        super().__init__()
        self.edges = []
        self.faces = []

    def add(self, edge):
        """
        Add edge to collection
        :param edge:
        :return:
        """
        if isinstance(edge, Edge) is False:
            raise TypeError('Edge argument needs to be of type Edge.')

        contains_res = self.contains(edge)
        if contains_res is not None:
            return contains_res

        super().add(edge)
        return edge

    def contains(self, edge):
        """
        Check if edge exists in set.
        """

        if edge not in self:
            return None

        for e in self:
            if e.__eq__(edge):
                return e

        raise IndexError("Something went terribly wrong when using contains method in edge collection.")


class Edge:
    def __init__(self, vertex1, vertex2):
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.faces = []

    def __eq__(self, other):

        if self.vertex1.index == other.vertex1.index and self.vertex2.index == other.vertex2.index:
            return True
        if self.vertex2.index == other.vertex1.index and self.vertex1.index == other.vertex2.index:
            return True

        return False

    def __hash__(self):
        h = hash(self.vertex1.z() + self.vertex2.z())
        return h

    def associate_with_face(self, face):
        if face not in self.faces:
            self.faces.append(face)
        else:
            raise STL_LEAK_EXCEPTION('The model contains leaks, and is broken beyond repair. '
                                     'Reduced vertex proximity tolerance may in some cases resolve the issue. '
                                     f'Vertex.proximity_tolerance currently set to: {Vertex.proximity_tolerance}. '
                                     'If you do not intend to utilize edges: load the STL with ignore_edges=true')
