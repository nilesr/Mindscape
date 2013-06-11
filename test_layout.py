import random

import pygame
from pygame.locals import *
from OpenGL.GL import *

from vmath import Vector, Matrix
from scenegraph import *
from layout import *

pygame.init()

WIDTH, HEIGHT=640, 480
ASPECT=float(WIDTH)/HEIGHT
FOV=75

disp=pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE|OPENGL|DOUBLEBUF)
pygame.display.set_caption('Test:Scenegraph')
clock=pygame.time.Clock()
char=pygame.image.load('data/char.png')

glClearColor(0.2, 0.4, 0.4, 0)

cam=PerspectiveCamera(Vector(3, 3, 3), Vector(0, 0, 0), Vector(0, 1, 0), FOV, ASPECT, 0.1, 100)
sc=Scene(cam)
sc.modifications.add(ModBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA))
sc.modifications.add(ModTexFilter(GL_NEAREST, GL_NEAREST))
sc.modifications.add(ModTexWrap(GL_REPEAT, GL_REPEAT))
sc.enable.add(GL_DEPTH_TEST)
sc.enable.add(GL_BLEND)
sc.disable.add(GL_LIGHTING)

tex=Texture(char)

mesh=Mesh(Face(GL_QUADS, Vertex(Vector(-1, -1, 0.1), Vector(1, 0, 0), tex=Vector(0, 0)),
						 Vertex(Vector(1, -1, 0.1), Vector(0, 1, 0), tex=Vector(1, 0)),
						 Vertex(Vector(1, 1, -0.1), Vector(0, 0, 1), tex=Vector(1, 1)),
						 Vertex(Vector(-1, 1, -0.1), Vector(1, 1, 1), tex=Vector(0, 1))), texture=tex)
mesh.transform.rot=[0, Vector(0, 0, 1)]
mesh.enable.add(GL_TEXTURE_2D)
sc.children.append(mesh)

lines=Mesh(Face(GL_LINES, Vertex(Vector(-1, 0, 0), Vector(1, 0, 0)),
						  Vertex(Vector(1, 0, 0), Vector(1, 0, 0))),
		   Face(GL_LINES, Vertex(Vector(0, -1, 0), Vector(0, 1, 0)),
						  Vertex(Vector(0, 1, 0), Vector(0, 1, 0))),
		   Face(GL_LINES, Vertex(Vector(0, 0, -1), Vector(0, 0, 1)),
						  Vertex(Vector(0, 0, 1), Vector(0, 0, 1))))
lines.disable.add(GL_DEPTH_TEST)
lines.transform.pos=Vector(1.5, 0, 0)
mesh.children.append(lines)

spr=WSSprite(texture=tex)
lines.children.append(spr)

##test=SSSprite(texture=tex, center=True)
##sc.children.append(test)

con=Container(Grid(3, 2))
lbl=Label(*con.grid.CellPair(0, 0), text='Hello world!', fcol=Vector(1, 0, 0, 1), bcol=Vector(0.5, 0.5, 0, 0.5))
con.children.append(lbl)
lbl=Label(*con.grid.CellPair(1, 0), text='I\'m fine today', align=TALIGN.LEFT|TALIGN.TOP, fcol=Vector(1, 0, 0, 1), bcol=Vector(0.5, 0, 0, 0.5))
con.children.append(lbl)
lbl=Label(*con.grid.CellPair(1, 2), text='I\'m great thanks!', align=TALIGN.FILLY, fcol=Vector(1, 0, 0, 1), bcol=Vector(0, 0.5, 0, 0.5))
con.children.append(lbl)
lbl=Label(*con.grid.CellPair(1, 1), text='How are you?', align=TALIGN.FILLX, fcol=Vector(1, 0, 0, 1), bcol=Vector(0, 0, 0.5, 0.5))
con.children.append(lbl)
sc.children.append(con)

##print 'Viewport: ', glGetIntegerv(GL_VIEWPORT)

##print 'Textures:', Texture.ALL

while True:
##	print 'Residences:', glAreTexturesResident([i.id for i in Texture.ALL])
	for ev in pygame.event.get():
		if ev.type==QUIT or (ev.type==KEYDOWN and ev.key==K_ESCAPE):
			exit()
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	mesh.transform.rot[0]+=1
	if mesh.transform.rot[0]>=360:
		mesh.transform.rot[0]-=360
	with sc:
		sc.Render()
	pygame.display.flip()
	clock.tick(30)