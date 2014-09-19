#####################################################
# Grantland Hall <GrantlandHall@Berkeley.edu>       #
# August 2014                                       #
#                                                   #
# Classes abstracting PC Boards in Eagle.           #
# A Board has multiple Signals which each           #
# represent a unique electrical signal.             #
# Each Signal has multiple SignalVertex elements    #
# which determine the locations of bends in the     #
# dignal routing.                                   #
#                                                   #
#####################################################

from math import sin, cos

class SignalVertex:
    """Representation of a signal vertex."""
    def __init__(self, signal, x, y):
        self.signal = signal # Haven't decided if this is useful
        self.x = x
        self.y = y
    def __str__(self):
        return "({} {})".format(self.x, self.y)

class Signal:
    """Representation of a signal.
       Signal constructor requires a float width and
       an integer layer number."""
    @staticmethod
    def new_id():
        """Get a unique id for the signal"""
        global signal_id
        try:
            signal_id += 1
        except:
            signal_id = 0
        return signal_id
    def __init__(self, width, layer):
        if not isinstance(layer, (int, long)):
            raise TypeError("Layer must be an integer value!")
        self.vertices = []
        self.width = width
        self.layer = layer
        self.signal_id = Signal.new_id()
    def add(self, x, y):
        """Add SignalVertex to signal."""
        self.vertices.append( SignalVertex(self, x, y) )
    def draw(self):
        """Return Eagle syntax."""
        route = "LAYER {}\n".format(self.layer)
        for vertex in xrange(len(self.vertices)-1):
            route += "WIRE 'RTE{s_id}' {vert1} {width}mm {vert2}\n".format(
                    s_id = self.signal_id, width = self.width,
                    vert1 = self.vertices[vertex],
                    vert2 = self.vertices[vertex + 1])
        return route
    def r_theta(self, r, theta):
        """Creates a new SignalVertex with offset
            (r, theta) from the last SignalVertex.
        """
        if len(self.vertices) == 0:
            raise IndexError((
                "r_theta() must reference an existing point. "
                "Signal {s_id} had no vertices."
                ).format(s_id = self.signal_id) )
        last_point = self.vertices[-1]
        new_x = last_point.x + r*cos(theta)
        new_y = last_point.y + r*sin(theta)
        self.add(new_x, new_y)

class Footprint:
    """Representation of a package footprint."""
    def __init__(self, name, package, library, orientation):
        """Representation of a footprint.

        Arguments:
        name -- Unique name Eagle will call this instance.
        package -- The name of the package in your eagle Lib.
        library -- The Eagle library which contains your package.
        orientation -- R<rad> for rotation <rad> radians.
                MR<rad> rotates AND Mirrors the footprint.
        """
        self.name = name
        self.package = package
        self.library = library
        self.orientation = orientation
    def place(self):
        return "ADD '{name}' {package}@{library} {orientation}".format(
                name = self.name, package = self.package,
                library = self.library, orientation = self.orientation
                )

class Board:
    """Representation of a PCB"""
    def __init__(self, outfile='generated_PCB.src'):
        """ Output filetype should be .src for use by
            Eagle's script functionality.
        """
        self.signals = []
        self.footprints = []
        self.outfile = outfile
    def add(self, thing):
        """Add signals and Footprints to boards."""
        if isinstance(thing, Signal):
            self.signals.append(thing)
        elif isinstance(thing, Footprint):
            self.footprints.append(thing)
        else:
            raise TypeError("Added object must be a Signal or a device footprint.")
    def draw(self):
        """Draw PCBoard and output to file"""
        f = open(self.outfile, 'w')
        for signal in self.signals:
            f.write( signal.draw() )
        for footprint in self.footprints:
            f.write( footprint.place() )

