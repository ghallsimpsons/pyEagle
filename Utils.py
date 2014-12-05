from Eagle import SignalVertex
import math

def distance(p1, p2):
    """ Returns the distance between two points."""
    coord1 = to_coord(p1)
    coord2 = to_coord(p2)
    return math.sqrt( (coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2 )

def distance_theta(p1, p2, theta):
    """ This function calculates the theta component between two points,
        the complementary component being orthogonal to theta.
    """
    coord1 = to_coord(p1)
    coord2 = to_coord(p2)
    dist = distance(p1, p2)
    angle = math.atan2(coord2[1]-coord1[1], coord2[0]-coord1[0])
    a_diff = theta - angle
    projected = dist*math.cos(a_diff)
    return projected

def project(x, y, theta_f, theta_i=0):
    """ Projects the x and y components along theta_i onto the axes rotated by
        theta_f-theta_i."""
    d_theta = theta_i - theta_f 
    x_r = x*math.cos(d_theta)-y*math.sin(d_theta)
    y_r = x*math.sin(d_theta)+y*math.cos(d_theta)
    return (x_r, y_r)

def to_coord(point):
    """ Converts a 2-tuple, 2-list or SignalVertex to a 2-tuple."""
    if isinstance(point, (list,tuple)) and len(point)==2:
        return tuple(point)
    elif isinstance(point, SignalVertex):
        return point.coord()
    raise TypeError("Points must be either a two-tuple or SignalVertex.")
