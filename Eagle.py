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

class SignalVertex:
    """Representation of a signal vertex."""
    def __init__(self, signal, x, y):
        self.signal = signal # Haven't decided if this is useful
        self.x = x
        self.y = y
    def __str__(self):
        return "({} {})".format(self.x, self.y)

class Signal:
    """Representation of a signal."""
    @staticmethod
    def new_id():
        global signal_id
        try:
            signal_id += 1
        except:
            signal_id = 0
        return signal_id
    def __init__(self, width, layer):
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


