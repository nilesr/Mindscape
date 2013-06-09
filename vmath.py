'''
mindscape -- Mindscape Engine
vmath -- Vector Math

This module defines some useful vector and matrix math, implemented generally
in numpy for speed.
'''

import numpy

class Vector(numpy.ndarray):
    def __new__(mcs, *args):
        inst=numpy.ndarray.__new__(mcs, (len(args),), numpy.float64)
        inst[:]=args
        return inst
    def _get_x(self):
        return self[0]
    def _set_x(self, val):
        self[0]=val
    def _get_y(self):
        return self[1]
    def _set_y(self, val):
        self[1]=val
    def _get_z(self):
        return self[2]
    def _set_z(self, val):
        self[2]=val
    def _get_w(self):
        return self[3]
    def _set_w(self, val):
        self[3]=val
    x=property(_get_x, _set_x)
    y=property(_get_y, _set_y)
    z=property(_get_z, _set_z)
    w=property(_get_w, _set_w)
    def length(self):
        return numpy.sqrt(self.dot(self))
    def unit(self):
        return self/self.length()
    def cross(self, other):
        if len(self)!=len(other)!=3:
            raise ValueError('Cross product only defined in 3 (and 7) dimensions.')
        return type(self)(self.y*other.z-self.z*other.y,
                          self.z*other.x-self.x*other.z,
                          self.x*other.y-self.y*other.x)
    def _ToX(self, x, fast=False):
        if fast and len(self)==x:
            return self
        inst=numpy.zeros((x,))
        if x>=4:
            inst[3]=1 #W is, by default, 1
        inst[:len(self)]=self
        return type(self)(*inst)
    def To2(self):
        return self._ToX(2)
    def To3(self):
        return self._ToX(3)
    def To4(self):
        return self._ToX(4)
    def FastTo2(self):
        return self._ToX(2, True)
    def FastTo3(self):
        return self._ToX(3, True)
    def FastTo4(self):
        return self._ToX(4, True)
                        
class Matrix(numpy.matrix):
    @classmethod
    def Rotation(cls, angle, axis): #XXX Only 3D rotations now.
        d=axis.unit()
        dd=numpy.outer(d, d)
        i=numpy.eye(3, dtype=numpy.float64)
        skew=numpy.array([[0, d[2], -d[1]], [-d[2], 0, d[0]], [d[1], -d[0], 0]], numpy.float64)
        return cls(ddt+numpy.cos(angle)*(i-ddt)+numpy.sin(angle)*skew)
    @classmethod
    def Translation(cls, vec):
        v=vec.To3()
        return cls([[1, 0, 0, v.x], [0, 1, 0, v.y], [0, 0, 1, v.z], [0, 0, 0, 1]])
    @classmethod
    def Scale(cls, vec):
        v=vec.To4()
        return cls([[v.x, 0, 0, 0], [0, v.y, 0, 0], [0, 0, v.z, 0], [0, 0, 0, v.w]])
    def _ToX(self, x, fast=False):
        if fast and len(self)==x:
            return self
        inst=type(self)(numpy.eye(x))
        inst[:len(self), :len(self)]=self
        return inst
    def To2(self):
        return self._ToX(2)
    def To3(self):
        return self._ToX(3)
    def To4(self):
        return self._ToX(4)
    def FastTo2(self):
        return self._ToX(2, True)
    def FastTo3(self):
        return self._ToX(3, True)
    def FastTo4(self):
        return self._ToX(4, True)