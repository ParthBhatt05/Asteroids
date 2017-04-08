from __future__ import division

class Quadratic(object):
    def __init__(self, p0, p1, p2, tmax):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.tmax = tmax

    def B(self, t):
        t = t / self.tmax
        v =  (1-t)**2*self.p0 + 2*(1-t)*t*self.p1 + t**2*self.p2
        return v