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

from math import sin, cos, tan, pi

class SignalVertex:
    """Representation of a signal vertex."""
    def __init__(self, signal, x, y):
        self.signal = signal # Haven't decided if this is useful
        self.x = x
        self.y = y
    def __str__(self):
        return "({} {})".format(self.x, self.y)
    def coord(self):
        return (self.x, self.y)

# Utils depents on SignalVertex
from Utils import distance_theta, project

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
    def __init__(self, width, layer, bend=2):
        """Arguments:

        width -- Trace width in mm
        layer -- Board layer to place trace
        bend -- Bend type, see: http://web.mit.edu/xavid/arch/i386_rhel4/help/86.htm
        """
        if not isinstance(layer, (int, long)):
            raise TypeError("Layer must be an integer value!")
        if not isinstance(bend, (int, long)) or bend < 0 or bend > 7:
            raise TypeError("Bend must be integer between 0 and 7! See \
                    http://web.mit.edu/xavid/arch/i386_rhel4/help/86.htm")
        self.vertices = []
        self.width = width
        self.layer = layer
        self.signal_id = Signal.new_id()
        self.bend = bend
    # Alias for the last vertex
    @property
    def last(self):
        return self.vertices[-1]
    @last.setter
    def last(self,value):
        self.vertices[-1]=value
    def add(self, x, y):
        """Add SignalVertex to signal."""
        self.vertices.append( SignalVertex(self, x, y) )
    def draw(self):
        """Return Eagle syntax."""
        route = "LAYER {}\n".format(self.layer)
        route += "SET WIRE_BEND {};\n".format(self.bend)
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

def FootprintFactory(package, library):
    """Creates a Factory for a particular footprint.

    Arguments:
    package -- The name of the package in your eagle Lib.
    library -- The Eagle library which contains your package.
    """
    class Footprint: 
        """Representation of a footprint type."""
        def __init__(self, name, orientation, location):
            """An individual instance of the degined footprint.

            Arguments:
            name -- Unique name Eagle will call this instance.
            orientation -- R<deg> for rotation <deg> degrees.
                MR<deg> rotates AND Mirrors the footprint.
            location -- (x, y) tuple, dimensions in mm
            """
            self.name = name
            self.orientation = orientation
            self.location = location
        def place(self):
            create = "ADD '{name}' {package}@{library} {orientation}".format(
                    name = self.name, package = self.package,
                    library = self.library, orientation = self.orientation
                )
            move = "MOVE {name} {x} {y}".format(
                    name = self.name, x = self.location[0],
                    y = self.location[1]
                )
            return "{create}\n{move}\n".format(create = create, move = move)

    Footprint.package = package
    Footprint.library = library

    return Footprint

class Board:
    """Representation of a PCB"""
    def __init__(self, outfile='generated_PCB.scr'):
        """ Output filetype should be .scr for use by
            Eagle's script functionality.
        """
        self.signals = []
        self.footprints = []
        self.outfile = outfile
    def add(self, thing):
        """Add signals and Footprints to boards."""
        if isinstance(thing, Signal):
            self.signals.append(thing)
        else:
            self.footprints.append(thing)
    def draw(self):
        """Draw PCBoard and output to file"""
        f = open(self.outfile, 'w')
        for signal in self.signals:
            f.write( signal.draw() )
        for footprint in self.footprints:
            f.write( footprint.place() )

class SignalGroup:
    """ The SignalGroup class allows for easy operations on closely related
        signals. Most operations will produce unexpected results if the signals
        are not parallel.
    """
    def __init__(self, signals):
        self.signals = signals
    def add(self, signal):
        self.signals.append(signal)
    def remove(self, signal):
        """ Remove signal by reference, index, or range as a tuple."""
        if isinstance(signal, (int, long)):
            del self.signals[signal]
        elif isinstance(signal, Signal):
            self.signals.remove(Signal)
        elif isinstance(signal, tuple) and len(signal)==2:
            del self.signals[signal[0]:signal[1]]
        else:
            raise TypeError("Argument must be a Signal, index, or tuple of ints")
    def elbow(self, theta_i, theta_f, distance=0, final_spacing=None, fixed=0):
        """ Bends signals in group from theta_i to theta_f.
            If a distance is provided, the traces will be extended that
            distance in the given orientation. Final spacing is a size
            N-1 list of distances which will convert the initial spacing
            to a new final spacing at the new orientation. If not provided,
            the initial spacing is preserved. The first element of traces is
            left stationary, unless invert=True (useful for symetric operations).
            All other traces are extended as necessary.
            Note: This function will misbehave if you provide an
            incorrect initial angle, or if the traces are not in correct order.
        """
        signals = self.signals
        init_spacing = [distance_theta(signals[i].last, signals[i+1].last, theta_i+pi/2) for i in xrange(len(signals)-1)]
        if (final_spacing != None and not isinstance(final_spacing, list) 
                and not len(final_spacing) == len(signals)-1):
            raise TypeError("final_spacing must be a list of distances between \
                    signals, i.e. a len(signals)-1 list.")
        elif final_spacing == None:
            final_spacing = init_spacing


        """ First, let theta_i = 0. Then delta_dist = final_spacing*cos(theta_f)
            - (init_spacing-final_spacing*cos(theta_f))*cot(pi/2-theta_f)
            We then project along -theta_i (equivalent to projecting theta_i onto
            theta = 0, which is what we want).
        """
        d_theta = theta_f - theta_i
        fixed_init_d = sum(init_spacing[:fixed])
        fixed_final_d = sum(final_spacing[:fixed])
        d = fixed_final_d*cos(d_theta) - \
            (fixed_init_d-fixed_final_d) \
            / tan(pi/2-d_theta)
        x_norm, y_norm = project(d, 0, theta_i, theta_f)
        signals[0].last.x -= x_norm
        signals[0].last.y -= y_norm
        base_coords = signals[0].last.coord()
        for i in xrange(len(init_spacing)):
            d = final_spacing[i]*cos(d_theta) - \
                (init_spacing[i]-final_spacing[i]*sin(d_theta)) \
                / tan(pi/2-d_theta)
            x_diff, y_diff = map(sum,zip(project(0, d, 0, theta_i-pi/2),project(init_spacing[i], 0, 0, theta_i-pi/2)))
            signals[i+1].last.x = base_coords[0] - x_diff
            signals[i+1].last.y = base_coords[1] - y_diff
            base_coords = signals[i+1].last.coord()
        self.grouped_r_theta(distance, theta_f, fixed)
    def grouped_r_theta(self, r, theta, center):
        """ Runs the center signal a distance r, and runs other signals to align
            with the first."""
        center = self.signals[center].last.coord()
        for sig in self.signals:
            delta = distance_theta(center, sig.last.coord(), theta)
            sig.r_theta(r-delta, theta)
