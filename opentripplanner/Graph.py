import os.path
from org.opentripplanner.routing.impl import InputStreamGraphSource
from java.io import File
from org.opentripplanner.routing.graph.Graph import LoadLevel

class Graph:
    """Represents an OpenTripPlanner graph"""

    def __init__(self, graph, rID):
        """
        Read the graph at the location specified by Graph.
        This function is also used internally to wrap an org.opentripplanner.routing.Graph, and
        can be called that way as well.
        """

        if isinstance(graph, str):
            # We need to load the graph from a file
            if not os.path.exists(graph):
                raise IOError, 'No such file or directory %s' % graph

            if os.path.isdir(graph):
                path = graph

            else:
                # must be a file
                path = os.path.dirname(graph)
                
            # print 'path is %s | graph is %s | rID is %s' % (path, graph, rID)

            isgs = InputStreamGraphSource.newFileGraphSource(rID, File(path), LoadLevel.FULL)
            isgs.reload(True, False)
            self._graph = isgs.router.graph

            # workaround for not having any graph service
            # self._graph.routerId = hex(id(self))

        else:
            # We're wrapping a graph
            self._graph = graph

    def getId(self):
        return '%s_%s' % (self._graph.routerId, id(self))
