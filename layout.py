'''
.. mindscape -- Mindscape Engine
wm -- Window Manager
====================

This module provides an interface to a simple layout manager which is entirely
compatible with the scenegraph (provided that it is rendered after 3D geometry
and with the depth test turned off). The layout manager is a *tiling* manager,
which means that it deals with grids.
'''

import pygame
from OpenGL.GL import *

from vmath import Vector
from scenegraph import Renderable, Texture

class LayoutCell(object):
	def __init__(self, weight=1.0, fixed=0):
		self.weight=weight
		self.fixed=fixed
		self.offset=-1
		self.size=-1

class LayoutVector(object):
	def __init__(self, *cells):
		if len(cells)==1 and isinstance(cells[0], (int, long)):
			self.cells=[LayoutCell() for i in xrange(cells[0])]
		else:
			self.cells=list(cells)
	def Compute(self, dim):
		dim-=sum([i.fixed for i in self.cells]) #Remove fixed allocations from weighting
		wtotal=sum([i.weight for i in self.cells])
		offset=0
		for cell in self.cells:
			cell.offset=offset
			cell.size=cell.fixed+(dim*cell.weight/wtotal)
			offset+=cell.size
	def __getitem__(self, idx):
		return self.cells[idx]

class Grid(object):
	def __init__(self, rows, cols):
		self.rows=(LayoutVector(rows) if isinstance(rows, (int, long)) else rows)
		self.cols=(LayoutVector(cols) if isinstance(cols, (int, long)) else cols)
	def Compute(self, dims):
		self.rows.Compute(dims.x)
		self.cols.Compute(dims.y)
	def CellPair(self, x, y):
		return self.cols[x], self.rows[y]

class Widget(Renderable):
	def __init__(self, xcell, ycell, fcol=None, bcol=None, **kwargs):
		super(Widget, self).__init__(**kwargs)
		self.xcell=xcell
		self.ycell=ycell
		self.fcol=fcol
		self.bcol=bcol
	@property
	def pos(self):
		return Vector(self.xcell.offset, self.ycell.offset)
	@property
	def size(self):
		return Vector(self.xcell.size, self.ycell.size)
	def PushState(self):
		glPushAttrib(GL_VIEWPORT_BIT)
		glViewport(*([int(i) for i in self.pos]+[int(i) for i in self.size]))
	def PopState(self):
		glPopAttrib()

class Container(Widget):
	def __init__(self, grid, xcell=None, ycell=None, **kwargs):
		super(Container, self).__init__(xcell, ycell, **kwargs)
		self.grid=grid
	def PushState(self):
		if self.xcell is None or self.ycell is None:
			#Initialize this as if we are a master layout (we probably are)
			glMatrixMode(GL_PROJECTION)
			glPushMatrix()
			glLoadIdentity()
			glMatrixMode(GL_MODELVIEW)
			glPushMatrix()
			glLoadIdentity()
			self.grid.Compute(Vector(*(glGetIntegerv(GL_VIEWPORT)[2:])))
		else:
			self.grid.Compute(self.size)
			super(Container, self).PushState() #Just do what every other widget does
	def PopState(self):
		if self.xcell is None or self.ycell is None:
			glMatrixMode(GL_PROJECTION)
			glPopMatrix()
			glMatrixMode(GL_MODELVIEW)
			glPopMatrix()
		else:
			super(Container, self).PopState()
	def Render(self):
		self.RenderChildren()

class TALIGN:
	LEFT=0x01
	CENTER=0x00
	RIGHT=0x02
	TOP=0x04
	MIDDLE=0x00
	BOTTOM=0x08
	FILLX=LEFT|RIGHT
	FILLY=TOP|BOTTOM

class Label(Widget):
	def  __init__(self, xcell, ycell, text='', align=0, font=None, **kwargs):
		super(Label, self).__init__(xcell, ycell, **kwargs)
		self.text=text
		self._oldtext=None
		self.align=align
		self.font=(pygame.font.SysFont(pygame.font.get_default_font(), 30) if font is None else font)
		self.tex=None
	def Render(self):
		glPushAttrib(GL_ENABLE_BIT)
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_DEPTH_TEST)
		if self.bcol is not None:
			glColor4d(*self.bcol.FastTo4())
			glRectdv((-1, -1), (1, 1))
		if self.text:
			if self.text is not self._oldtext:
				fcol=self.fcol
				if fcol is None:
					fcol=Vector(1, 1, 1)
				tsurf=self.font.render(self.text, True, tuple(255*fcol.FastTo3()))
				if self.tex is None:
					self.tex=Texture()
				self.tex.surf=tsurf
				self.tex.Reload()
				self._oldtext=self.text
			tsz=Vector(*self.tex.surf.get_size())
			vsz=Vector(*(glGetIntegerv(GL_VIEWPORT)[2:]))
			csz=tsz/vsz
			minima=-csz
			maxima=csz.copy()
			if self.align&TALIGN.LEFT:
				minima.x=-1
				maxima.x-=1-csz.x
			if self.align&TALIGN.RIGHT:
				maxima.x=1
				if not self.align&TALIGN.LEFT:
					minima.x+=1-csz.x
			if self.align&TALIGN.BOTTOM:
				minima.y=-1
				maxima.y-=1-csz.y
			if self.align&TALIGN.TOP:
				maxima.y=1
				if not self.align&TALIGN.BOTTOM:
					minima.y+=1-csz.y
			glEnable(GL_TEXTURE_2D)
			self.tex.Reload()
			#self.tex.Apply()
			glColor4d(1, 1, 1, 1)
			glBegin(GL_QUADS)
			glTexCoord2d(0, 0)
			glVertex2d(minima.x, minima.y)
			glTexCoord2d(1, 0)
			glVertex2d(maxima.x, minima.y)
			glTexCoord2d(1, 1)
			glVertex2d(maxima.x, maxima.y)
			glTexCoord2d(0, 1)
			glVertex2d(minima.x, maxima.y)
			glEnd()
		glPopAttrib()