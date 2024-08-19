import math
from typing import Self, overload

#"pip install PyOpenGL"
import OpenGL.GL as GL

from common import Color, vec2f



class Base:
	__slots__ = ( "color", )

	def __init__( self:Self, color:Color ):
		self.color = tuple(color)

class Box(Base):
	__slots__ = ( "lo", "hi" )

	@overload
	def __init__( self:Self, color:Color, lo:vec2f,hi:vec2f ): ...
	@overload
	def __init__( self:Self, color:Color, lo:vec2f,hi:vec2f, dilate:float ): ...
	@overload
	def __init__( self:Self, color:Color, center:vec2f,radius:float ): ...
	def __init__( self:Self, color:Color, *args ):
		Base.__init__( self, color )
		match args:
			case [ tuple() as lo, tuple() as hi ]:
				self.lo:vec2f = tuple(lo)
				self.hi:vec2f = tuple(hi)
			case [ tuple() as lo, tuple() as hi, float() as dilate ]:
				self.lo:vec2f = ( lo[0]+dilate, lo[1]+dilate )
				self.hi:vec2f = ( hi[0]-dilate, hi[1]-dilate )
			case [ tuple() as center, float() as radius ]:
				self.lo:vec2f = ( center[0]-radius, center[1]-radius )
				self.hi:vec2f = ( center[0]+radius, center[1]+radius )

	def draw( self:Self ):
		GL.glColor3f( *self.color )
		GL.glBegin(GL.GL_TRIANGLE_STRIP)
		GL.glVertex2f( self.lo[0], self.lo[1] )
		GL.glVertex2f( self.hi[0], self.lo[1] )
		GL.glVertex2f( self.lo[0], self.hi[1] )
		GL.glVertex2f( self.hi[0], self.hi[1] )
		GL.glEnd()

class Circle(Base):
	def __init__( self:Self, color:Color, center:vec2f,radius:float, N:int=100 ):
		Base.__init__( self, color )
		self.center:vec2f = tuple(center)
		self.radius       = radius
		self.N = N

	def draw( self:Self ):
		GL.glColor3f( *self.color )
		GL.glBegin(GL.GL_TRIANGLE_FAN)
		factor = math.tau / self.N
		for k in range(self.N):
			angle = k * factor
			GL.glVertex2f(
				self.center[0] + self.radius*math.cos(angle),
				self.center[1] + self.radius*math.sin(angle)
			)
		GL.glEnd()

class Polygon(Base):
	__slots__ = ( "points", )

	def __init__( self:Self, color:Color, points:list[vec2f] ):
		Base.__init__( self, color )
		self.points = list(points)

	def draw( self:Self ):
		GL.glColor3f( *self.color )
		GL.glBegin(GL.GL_POLYGON)
		for point in self.points:
			GL.glVertex2f( *point )
		GL.glEnd()

class Capsule(Base):
	__slots__ = ( "p0","p1", "radius", "half_N" )

	def __init__( self:Self, color:Color, p0:vec2f,p1:vec2f,radius:float, N:int=100 ):
		Base.__init__( self, color )
		self.p0:vec2f = tuple(p0)
		self.p1:vec2f = tuple(p1)
		self.radius = radius
		self.half_N = N // 2

	def draw( self:Self ):
		vec = ( self.p1[0]-self.p0[0], self.p1[1]-self.p0[1] )
		l = math.hypot( vec[0], vec[1] )

		points:list[vec2f] = []
		for k in range(self.half_N):
			angle = k * math.pi/(self.half_N-1)
			points.append(( self.radius*math.cos(angle), self.radius*math.sin(angle) ))
		for k in range( self.half_N-1, -1,-1 ):
			angle = k * -math.pi/(self.half_N-1)
			points.append(( self.radius*math.cos(angle), self.radius*math.sin(angle)-l ))

		GL.glColor3f( *self.color )
		GL.glPushMatrix()
		GL.glTranslatef( *self.p0, 0.0 )
		GL.glRotatef( math.degrees(math.atan2(vec[1],vec[0]))+90, 0.0,0.0,1.0 )
		GL.glBegin(GL.GL_TRIANGLE_FAN)
		for pt in points: GL.glVertex2f( *pt )
		GL.glEnd()
		GL.glPopMatrix()

class Diamond(Base):
	__slots__ = ( "center", "radius" )

	def __init__( self:Self, color:Color, center:vec2f,radius:float ):
		Base.__init__(self, color)
		self.center = tuple(center)
		self.radius = radius

	def draw( self:Self ):
		GL.glColor3f( *self.color )
		GL.glBegin(GL.GL_QUADS)
		GL.glVertex2f( self.center[0]-self.radius, self.center[1] )
		GL.glVertex2f( self.center[0], self.center[1]-self.radius )
		GL.glVertex2f( self.center[0]+self.radius, self.center[1] )
		GL.glVertex2f( self.center[0], self.center[1]+self.radius )
		GL.glEnd()
