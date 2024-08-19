from typing import Self

#"pip install PyOpenGL"
import OpenGL.GL as GL

from common import *
import subpixel



class Base:
	def __init__( self:Self,
		name:str, scale:float=1.0,shift:tuple[float,float]=(1.0,1.0)
	):
		self.name = name

		self.tile_subpixels:list[subpixel.Base] = []
		self.tile_scale = scale
		self.tile_shift = tuple(shift)

		self.grids = []

		self.view_scale = 4.0
		self.view_shift = ( 0.0, 0.0 )

	def add( self:Self, sub:subpixel.Base ):
		self.tile_subpixels.append(sub)

	def add_grid( self:Self, rep:tuple[int,int], shift:vec2f=(0.0,0.0), color:Color=PURE_CYAN ):
		self.grids.append(( tuple(rep), color, shift ))

	def draw( self:Self ):
		for     j in range( -1, 8, 1 ):
			for i in range( -1, 8, 1 ):
				GL.glPushMatrix()
				GL.glTranslatef(
					self.view_shift[0] + self.tile_shift[0]*i,
					self.view_shift[1] + self.tile_shift[1]*j,
					0.0
				)
				GL.glScalef( self.tile_scale, self.tile_scale, 1.0 )
				for sub in self.tile_subpixels:
					sub.draw()
				GL.glPopMatrix()

	def draw_grid( self:Self, size_view:float, line_width_px:float ):
		( x,y, w,h ) = GL.glGetIntegerv(GL.GL_VIEWPORT)
		assert w == h
		units_per_px = size_view / w
		d = units_per_px * 0.5*line_width_px

		GL.glLineWidth(line_width_px)

		for rep, color, shift in self.grids:
			GL.glColor3f( *color )
			for     j in range( rep[1] ):
				for i in range( rep[0] ):
					GL.glPushMatrix()
					GL.glTranslatef(
						self.view_shift[0] + shift[0] + i,
						self.view_shift[1] + shift[1] + j,
						0.0
					)

					GL.glBegin(GL.GL_LINES)
					GL.glVertex2f(  -d, 0.0 ); GL.glVertex2f( 1.0+d, 0.0 )
					GL.glVertex2f(  -d, 1.0 ); GL.glVertex2f( 1.0+d, 1.0 )
					GL.glVertex2f( 0.0,  -d ); GL.glVertex2f( 0.0, 1.0+d )
					GL.glVertex2f( 1.0,  -d ); GL.glVertex2f( 1.0, 1.0+d )
					GL.glEnd()

					GL.glPopMatrix()



class SquareBase(Base):
	def __init__( self:Self,
		name:str, scale:float=1.0,shift:tuple[float,float]=(1.0,1.0)
	):
		Base.__init__( self, "sq_"+name, scale,shift )

class PenTileBase(Base):
	def __init__( self:Self,
		name:str, scale:float=1.0,shift:tuple[float,float]=(1.0,1.0)
	):
		Base.__init__( self, "pent_"+name, scale,shift )

class FilterBase(Base):
	def __init__( self:Self,
		name:str, scale:float=1.0,shift:tuple[float,float]=(1.0,1.0)
	):
		Base.__init__( self, "filt_"+name, scale,shift )

class TriangleBase(Base):
	def __init__( self:Self,
		name:str, scale:float=1.0,shift:tuple[float,float]=(1.0,1.0)
	):
		Base.__init__( self, "tri_"+name, scale,shift )



class SquareBasic(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "Basic" )
		self.add(subpixel.Box( WHITE, (0.0,0.0),(1.0,1.0) ))
		self.add_grid( (1,1), (0.0,0.0), PURE_RED )

class SquareRGB(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "RGB", 1.0/6.0 )
		self.add(subpixel.Capsule( RED  , (1.0,1.2),(1.0,4.8), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (3.0,1.2),(3.0,4.8), 0.72 ))
		self.add(subpixel.Capsule( BLUE , (5.0,1.2),(5.0,4.8), 0.72 ))
		self.add_grid((1,1))

class SquareBGR(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "BGR", 1.0/6.0 )
		self.add(subpixel.Capsule( BLUE , (1.0,1.2),(1.0,4.8), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (3.0,1.2),(3.0,4.8), 0.72 ))
		self.add(subpixel.Capsule( RED  , (5.0,1.2),(5.0,4.8), 0.72 ))
		self.add_grid((1,1))

class SquareAlternateRBG(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "AlternateRBG", 1.0/6.0, (1.0,2.0) )

		self.add(subpixel.Capsule( RED  , (1.0,    1.2),(1.0,    4.8), 0.72 ))
		self.add(subpixel.Capsule( BLUE , (3.0,    1.2),(3.0,    4.8), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (5.0,    1.2),(5.0,    4.8), 0.72 ))

		self.add(subpixel.Capsule( GREEN, (1.0,6.0+1.2),(1.0,6.0+4.8), 0.72 ))
		self.add(subpixel.Capsule( BLUE , (3.0,6.0+1.2),(3.0,6.0+4.8), 0.72 ))
		self.add(subpixel.Capsule( RED  , (5.0,6.0+1.2),(5.0,6.0+4.8), 0.72 ))

		self.add_grid((1,2))

class SquareRGBChevron(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "ChevronRGB", 1.0/15.0 )

		radius = 1.5
		dx = -2.5
		dy =  1.875 #15.0/8.0

		self.add(subpixel.Capsule( RED,   ( 2.5+dx,     dy),( 7.0+dx,7.5), radius ))
		self.add(subpixel.Capsule( RED,   ( 2.5+dx,15.0-dy),( 7.0+dx,7.5), radius ))

		self.add(subpixel.Capsule( GREEN, ( 7.5+dx,     dy),(12.0+dx,7.5), radius ))
		self.add(subpixel.Capsule( GREEN, ( 7.5+dx,15.0-dy),(12.0+dx,7.5), radius ))

		self.add(subpixel.Capsule( BLUE,  (12.5+dx,     dy),(17.0+dx,7.5), radius ))
		self.add(subpixel.Capsule( BLUE,  (12.5+dx,15.0-dy),(17.0+dx,7.5), radius ))

		self.add_grid((1,1))

class SquareRGBY(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "RGBY", 1.0/4.0 )
		def scale_in( x:float, y:float ):
			x = (x-2.0)*0.95 + 2.0
			y = (y-2.0)*0.95 + 2.0
			return ( x, y )
		for     j in range(2):
			for i in range(4):
				col = ( RED, GREEN, BLUE, YELLOW )[i]
				lo = scale_in( i+0.07, 2*j+0.07 )
				hi = scale_in( i+0.93, 2*j+1.93 )
				self.add(subpixel.Box( col, lo,hi ))
		self.add_grid((1,1))

class SquareShiftRGBY(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "ShiftRGBY", 1.0/2.0, (2.0,2.0) )
		for     j in range(2):
			for i in range(4):
				col = ( RED,GREEN,BLUE,YELLOW, BLUE,YELLOW,RED,GREEN )[ 4*j + i ]
				dy = 0.0 if i%2==0 else 1.0
				lo = ( i+0.07, 2*j+0.07+dy )
				hi = ( i+0.93, 2*j+1.93+dy )
				self.add(subpixel.Box( col, lo,hi ))
		self.add_grid((1,1))

class SquareVRGB(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "VRGB", 1.0/6.0 )
		self.add(subpixel.Capsule( RED  , (1.2,1.0),(4.8,1.0), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (1.2,3.0),(4.8,3.0), 0.72 ))
		self.add(subpixel.Capsule( BLUE , (1.2,5.0),(4.8,5.0), 0.72 ))
		self.add_grid((1,1))

class SquareTiltVRGB(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "TiltVRGB", 1.0/12.0 )
		self.add(subpixel.Box( RED  , (2.0,2.0),( 5.5, 5.5) ))
		self.add(subpixel.Box( GREEN, (4.0,6.5),( 8.5,11.0) ))
		self.add(subpixel.Box( BLUE , (7.5,1.0),(10.0, 3.5) ))
		self.add_grid((1,1))

class SquareVBGR(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "VBGR", 1.0/6.0 )
		self.add(subpixel.Capsule( BLUE , (1.2,1.0),(4.8,1.0), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (1.2,3.0),(4.8,3.0), 0.72 ))
		self.add(subpixel.Capsule( RED  , (1.2,5.0),(4.8,5.0), 0.72 ))
		self.add_grid((1,1))

class SquareSStripeRGB(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "SStripeRGB", 1.0/6.0 )
		self.add(subpixel.Capsule( BLUE , (1.0,1.0),(1.0,5.0), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (3.0,1.5),(5.0,1.5), 0.72 ))
		self.add(subpixel.Capsule( RED  , (3.0,4.5),(5.0,4.5), 0.72 ))
		self.add_grid((1,1))

class SquareAlternateSStripeRGB(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "AlternateSStripeRGB", 1.0/6.0, (1.0,2.0) )

		self.add(subpixel.Capsule( BLUE , (1.0,    1.0),(1.0,    5.0), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (3.0,    1.5),(5.0,    1.5), 0.72 ))
		self.add(subpixel.Capsule( RED  , (3.0,    4.5),(5.0,    4.5), 0.72 ))

		self.add(subpixel.Capsule( BLUE , (5.0,6.0+1.0),(5.0,6.0+5.0), 0.72 ))
		self.add(subpixel.Capsule( GREEN, (1.0,6.0+1.5),(3.0,6.0+1.5), 0.72 ))
		self.add(subpixel.Capsule( RED  , (1.0,6.0+4.5),(3.0,6.0+4.5), 0.72 ))

		self.add_grid((1,2))

class SquareShiftSStripeRGB(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "ShiftSStripeRGB", 1.0/6.0, (2.0,2.0) )
		for     j in range(2):
			for i in range(2):
				x=i*6.0; y=j*6.0
				self.add(subpixel.Capsule( RED  , (3.0+x,1.5+y),(4.1+x,1.5+y), 0.72 ))
				self.add(subpixel.Capsule( GREEN, (3.0+x,4.5+y),(4.1+x,4.5+y), 0.72 ))
				y += ( 0.0, 1.8 )[ i ^ j ]
				self.add(subpixel.Capsule( BLUE , (0.75+x,0.75+y),(0.75+x,3.45+y), 0.48 ))
		self.add_grid((2,2))

class SquareXO(SquareBase):
	def __init__( self:Self ):
		SquareBase.__init__( self, "XO", 0.5, (3.0,3.0) )

		self.add(subpixel.Box( RED  , (1.0,1.0), 0.6 ))
		self.add(subpixel.Box( GREEN, (3.0,1.0), 0.6 ))
		self.add(subpixel.Box( BLUE , (5.0,1.0), 0.6 ))
		self.add(subpixel.Box( GREEN, (1.0,3.0), 0.6 ))
		self.add(subpixel.Box( BLUE , (3.0,3.0), 0.6 ))
		self.add(subpixel.Box( RED  , (5.0,3.0), 0.6 ))
		self.add(subpixel.Box( BLUE , (1.0,5.0), 0.6 ))
		self.add(subpixel.Box( RED  , (3.0,5.0), 0.6 ))
		self.add(subpixel.Box( GREEN, (5.0,5.0), 0.6 ))

		self.add_grid((3,3))

		self.view_scale = 6



class PenTileAlternateRGBG(PenTileBase):
	def __init__( self:Self ):
		PenTileBase.__init__( self, "AlternateRGBG", 1.0/6.0, (2.0,2.0) )
		for     j in range(2):
			for i in range(2):
				dx=6.0*i; dy=6.0*j
				if i == j:
					self.add(subpixel.Box( RED , (dx+2.0,dy+3.0), 1.5 ))
				else:
					self.add(subpixel.Box( BLUE, (dx+2.0,dy+3.0), 1.2 ))
				self.add(subpixel.Capsule( GREEN, (dx+5.0,dy+1.5),(dx+5.0,dy+4.5), 0.39 ))
		self.add_grid((2,2))

class PenTileAlternateRGBW(PenTileBase):
	def __init__( self:Self ):
		PenTileBase.__init__( self, "AlternateRGBW", 1.0/4.0, (2.0,2.0) )
		for     j in range(2):
			for i in range(2):
				dx=4.0*i; dy=4.0*j
				col0 = ( RED  , BLUE  )[ i ^ j ]
				col1 = ( GREEN, WHITE )[ i ^ j ]
				self.add(subpixel.Capsule( col0, (dx+1.0,dy+1.0),(dx+1.0,dy+3.0), 0.48 ))
				self.add(subpixel.Capsule( col1, (dx+3.0,dy+1.0),(dx+3.0,dy+3.0), 0.48 ))
		self.add_grid((2,2))

class PenTileDiamond(PenTileBase):
	def __init__( self:Self ):
		PenTileBase.__init__( self, "Diamond", 1.0/4.0, (2.0,2.0) )
		d = 0.08
		for     j in range(2):
			for i in range(2):
				dx=4.0*i; dy=4.0*j
				if i == j:
					self.add(subpixel.Diamond( RED  , (dx+3.0,dy+1.0), 1.04 ))
					self.add(subpixel.Capsule( GREEN, (dx+1.0-d,dy+3.0+d),(dx+1.0+d,dy+3.0-d), 0.56 ))
				else:
					self.add(subpixel.Diamond( BLUE , (dx+3.0,dy+1.0), 1.20 ))
					self.add(subpixel.Capsule( GREEN, (dx+1.0-d,dy+3.0-d),(dx+1.0+d,dy+3.0+d), 0.56 ))
		self.add_grid((2,2))

class PenTileDiamondOrthogonal(PenTileBase):
	def __init__( self:Self ):
		PenTileBase.__init__( self, "DiamondOrthogonal", 1.0/4.0 )
		self.add(subpixel.Diamond( RED  , (1.0,1.0), 0.6 ))
		self.add(subpixel.Diamond( GREEN, (3.0,1.0), 0.6 ))
		self.add(subpixel.Diamond( GREEN, (1.0,3.0), 0.6 ))
		self.add(subpixel.Diamond( BLUE , (3.0,3.0), 0.6 ))
		self.add_grid((1,1))



class FilterBayer2Base(FilterBase):
	def __init__( self:Self, name:str, colors:list[Color] ):
		FilterBase.__init__( self, name, 1.0/2.0, (2.0,2.0) )
		self.add(subpixel.Box( colors[0], (1.0,1.0), 0.8 ))
		self.add(subpixel.Box( colors[1], (3.0,1.0), 0.8 ))
		self.add(subpixel.Box( colors[2], (1.0,3.0), 0.8 ))
		self.add(subpixel.Box( colors[3], (3.0,3.0), 0.8 ))
		self.add_grid((2,2))
		self.view_scale = 8.0
class FilterGRBG(FilterBayer2Base):
	def __init__( self:Self ): FilterBayer2Base.__init__( self, "GRBG", [GREEN,RED,BLUE,GREEN] )
class FilterWRBG(FilterBayer2Base):
	def __init__( self:Self ): FilterBayer2Base.__init__( self, "WRBG", [WHITE,RED,BLUE,GREEN] )
class FilterCRBG(FilterBayer2Base):
	def __init__( self:Self ): FilterBayer2Base.__init__( self, "CRBG", [CYAN,RED,BLUE,GREEN] )
class FilterCYGM(FilterBayer2Base):
	def __init__( self:Self ): FilterBayer2Base.__init__( self, "CYGM", [CYAN,YELLOW,GREEN,MAGENTA] )
class FilterCYYM(FilterBayer2Base):
	def __init__( self:Self ): FilterBayer2Base.__init__( self, "CYYM", [CYAN,YELLOW,YELLOW,MAGENTA] )

class FilterBayer4Base(FilterBase):
	def __init__( self:Self, name:str, colors:list[Color] ):
		FilterBase.__init__( self, name, 1.0/2.0, (4.0,4.0) )
		for     j in range(4):
			for i in range(4):
				self.add(subpixel.Box( colors[j][i], (2*i+1,2*j+1), 0.8 ))
		self.add_grid((4,4))
		self.view_scale = 8.0
class FilterKodakRGBW4a(FilterBayer4Base):
	def __init__( self:Self ):
		FilterBayer4Base.__init__( self, "KodakRGBW4a", [
			[ WHITE, BLUE , WHITE, GREEN ],
			[ BLUE , WHITE, GREEN, WHITE ],
			[ WHITE, GREEN, WHITE, RED   ],
			[ GREEN, WHITE, RED  , WHITE ]
		] )
class FilterKodakRGBW4b(FilterBayer4Base):
	def __init__( self:Self ):
		FilterBayer4Base.__init__( self, "KodakRGBW4b", [
			[ GREEN, WHITE, RED  , WHITE ],
			[ GREEN, WHITE, RED  , WHITE ],
			[ BLUE , WHITE, GREEN, WHITE ],
			[ BLUE , WHITE, GREEN, WHITE ]
		] )
class FilterKodakRGBW4c(FilterBayer4Base):
	def __init__( self:Self ):
		FilterBayer4Base.__init__( self, "KodakRGBW4c", [
			[ GREEN, WHITE, RED  , WHITE ],
			[ BLUE , WHITE, GREEN, WHITE ],
			[ GREEN, WHITE, RED  , WHITE ],
			[ BLUE , WHITE, GREEN, WHITE ]
		] )

class FilterFujiXTrans(FilterBase):
	def __init__( self:Self ):
		FilterBase.__init__( self, "FujiXTrans", 1.0/2.0, (6.0,6.0) )
		x=0; y=0
		for ch in "GBGGRG\nRGRBGB\nGBGGRG\nGRGGBG\nBGBRGR\nGRGGBG":
			if ch == "\n":
				x=0; y+=1
			else:
				if   ch == "R": col = RED
				elif ch == "G": col = GREEN
				else          : col = BLUE
				self.add(subpixel.Box( col, (2*x+1,2*y+1), 0.6 ))
				x += 1
		self.add_grid((6,6))
		self.view_scale = 12.0

class FilterFujiEXR(FilterBase):
	def __init__( self:Self ):
		FilterBase.__init__( self, "FujiEXR", 1.0, (2.0,2.0) )
		for dx, dy in ( (0.0,0.0), (0.5,0.5) ):
			self.add(subpixel.Circle( RED  , (dx+0.5,dy+0.5), 0.25 ))
			self.add(subpixel.Circle( GREEN, (dx+1.5,dy+0.5), 0.25 ))
			self.add(subpixel.Circle( GREEN, (dx+0.5,dy+1.5), 0.25 ))
			self.add(subpixel.Circle( BLUE , (dx+1.5,dy+1.5), 0.25 ))
		self.add_grid( (2,2), (0.5,0.5), DARK_CYAN )
		self.add_grid( (2,2) )
		self.view_scale = 5.0

class FilterAlternateRGWRGB(FilterBase):
	def __init__( self:Self ):
		FilterBase.__init__( self, "AlternateRGWRGB", 1.0/6.0, (2.0,2.0) )

		x=0; y=0; bias=-0.12
		for ch in "RGWRGB\nRGBRGW":
			if ch == "\n":
				x=0; y+=1; bias=-bias
				continue

			if ch in "RGB":
				if   ch == "R":
					xx=2*x+1.0; r=0.60; col=RED
				elif ch == "G":
					xx=2*x+0.7; r=0.60; col=GREEN
				elif ch == "B":
					xx=2*x+0.7; r=0.90; col=BLUE
				self.add(subpixel.Capsule( col, (xx-bias,(4*y+1)*1.5),(xx+bias,(4*y+3)*1.5), r ))
			else:
				self.add(subpixel.Polygon( WHITE, [
					( (2*x-0.2)-2.0*bias, (10*y+1)*0.6 ),
					( (2*x+1.8)-2.0*bias, (10*y+1)*0.6 ),
					( (2*x+1.8)+2.0*bias, (10*y+9)*0.6 ),
					( (2*x-0.2)+2.0*bias, (10*y+9)*0.6 )
				] ))
			x += 1

		self.add_grid((2,2))



class TriangleHorizDotsRGB(TriangleBase):
	def __init__( self:Self ):
		SC = 0.5
		TriangleBase.__init__( self, "HorizDotsRGB", SC, (SC*3.0,SC*3.0**0.5) )

		dx=0.0; dy=0.5

		self.add(subpixel.Circle( RED  , (dx+0.0,dy+0.0), 0.42 ))
		self.add(subpixel.Circle( GREEN, (dx+1.0,dy+0.0), 0.42 ))
		self.add(subpixel.Circle( BLUE , (dx+2.0,dy+0.0), 0.42 ))

		self.add(subpixel.Circle( BLUE , (dx+0.5,dy+0.5*3.0**0.5), 0.42 ))
		self.add(subpixel.Circle( RED  , (dx+1.5,dy+0.5*3.0**0.5), 0.42 ))
		self.add(subpixel.Circle( GREEN, (dx+2.5,dy+0.5*3.0**0.5), 0.42 ))

		self.add_grid((3,3))

		self.view_scale = 4.0

class TriangleHorizDotsDiagonalRGB(TriangleBase):
	def __init__( self:Self ):
		SC = 1.0/3.0
		TriangleBase.__init__( self, "HorizDotsDiagonalRGB", SC, (SC*3.0,SC*3.0) )

		def box_at( color:Color, x:float,y:float ):
			if   color == RED  : rh = 0.55
			elif color == GREEN: rh = 0.50
			else               : rh = 0.60
			lo0 = ( x-0.42, y-rh   )
			hi0 = ( x+0.42, y-0.03 )
			lo1 = ( x-0.42, y+0.03 )
			hi1 = ( x+0.42, y+rh   )
			self.add(subpixel.Box( color, lo0,hi0 ))
			self.add(subpixel.Box( color, lo1,hi1 ))

		box_at( RED  ,  0.0,0.0 )
		box_at( GREEN,  1.0,0.0 )
		box_at( BLUE ,  2.0,0.0 )

		box_at( RED  ,  1.5,1.5 )
		box_at( GREEN, -0.5,1.5 )
		box_at( BLUE ,  0.5,1.5 )

		#self.add_grid((3,3))

		#self.view_scale = 4.0

class TriangleVertDotsRGB(TriangleBase):
	def __init__( self:Self ):
		SC = 0.5
		TriangleBase.__init__( self, "VertDotsRGB", SC, (SC*3.0**0.5,SC*3.0) )

		dy = 0.0
		dx = -0.5*3.0**0.5
		dx += 0.5*( 2.0 - 0.5*3.0**0.5 )

		self.add(subpixel.Circle( RED  , (dx+0.0,dy+0.0), 0.42 ))
		self.add(subpixel.Circle( GREEN, (dx+0.0,dy+1.0), 0.42 ))
		self.add(subpixel.Circle( BLUE , (dx+0.0,dy+2.0), 0.42 ))

		self.add(subpixel.Circle( BLUE , (dx+0.5*3.0**0.5,dy+0.5), 0.42 ))
		self.add(subpixel.Circle( RED  , (dx+0.5*3.0**0.5,dy+1.5), 0.42 ))
		self.add(subpixel.Circle( GREEN, (dx+0.5*3.0**0.5,dy+2.5), 0.42 ))

		self.add_grid((3,3))

		self.view_scale = 4.0

class TriangleVertDots23BGR(TriangleBase):
	def __init__( self:Self ):
		SC = 2
		TriangleBase.__init__( self, "VertDots23BGR", SC*1.0/24.0, (SC*18/24,SC*24/24) )

		def pix_r( x:float, y:float ):
			lo=(x-1.0,y-0.8); hi=(x+3.5,y+2.7)
			self.add(subpixel.Box( RED  , lo,hi ))
		def pix_g( x:float, y:float ):
			lo=(x-1.0,y-0.5); hi=(x+3.5,y+3.0)
			self.add(subpixel.Box( GREEN, lo,hi ))
		def pix_b( x:float, y:float ):
			lo=(x-1.0,y-2.7); hi=(x+3.5,y+2.3)
			self.add(subpixel.Box( BLUE , lo,hi ))

		dx=-2.8; dy=-3.1
		#dx=-2.8; dy=-7.0

		pix_g( dx+ 3.0, dy+ 4.0 )
		pix_b( dx+12.0, dy+ 8.0 )

		pix_r( dx+ 3.0, dy+12.0 )
		pix_g( dx+12.0, dy+16.0 )

		pix_b( dx+ 3.0, dy+20.0 )
		pix_r( dx+12.0, dy+24.0 )

		self.add_grid( (4,3), (0.0,0.0), DARK_CYAN )
		self.add_grid( (3,2), (0.0,0.0)            )

		self.view_scale = 7.0
		self.view_shift = ( 0.1, 0.1 )

class TriangleVertSetsRGB(TriangleBase):
	def __init__( self:Self ):
		TriangleBase.__init__( self, "VertSetsRGB", 1.0, (2.0,2.0) )

		def bars_at( x:float,y:float, sc:float ):
			sc = 1.0/6.0
			self.add(subpixel.Capsule( RED  , (1.0*sc+x,1.0*sc+y),(1.0*sc+x,5.0*sc+y), 0.72*sc ))
			self.add(subpixel.Capsule( GREEN, (3.0*sc+x,1.0*sc+y),(3.0*sc+x,5.0*sc+y), 0.72*sc ))
			self.add(subpixel.Capsule( BLUE , (5.0*sc+x,1.0*sc+y),(5.0*sc+x,5.0*sc+y), 0.72*sc ))
		bars_at( 0.0,0.0, 1.0 )
		bars_at( 0.0,1.0, 1.0 )
		bars_at( 1.0,0.5, 1.0 )
		bars_at( 1.0,1.5, 1.0 )

		self.add_grid((2,1))

		self.view_scale = 5.0



all_geoms:list[Base] = [
	SquareBasic(),
	SquareRGB(),
	SquareBGR(),
	SquareAlternateRBG(),
	SquareRGBChevron(),
	SquareRGBY(),
	SquareShiftRGBY(),
	SquareVRGB(),
	SquareTiltVRGB(),
	SquareVBGR(),
	SquareSStripeRGB(),
	SquareAlternateSStripeRGB(),
	SquareShiftSStripeRGB(),
	SquareXO(),

	PenTileAlternateRGBG(),
	PenTileAlternateRGBW(),
	PenTileDiamond(),
	PenTileDiamondOrthogonal(),

	FilterGRBG(),
	FilterWRBG(),
	FilterCRBG(),
	FilterCYGM(),
	FilterCYYM(),
	FilterKodakRGBW4a(),
	FilterKodakRGBW4b(),
	FilterKodakRGBW4c(),
	FilterFujiXTrans(),
	FilterFujiEXR(),
	FilterAlternateRGWRGB(),

	TriangleHorizDotsRGB(),
	TriangleHorizDotsDiagonalRGB(),
	TriangleVertDotsRGB(),
	TriangleVertDots23BGR(),
	TriangleVertSetsRGB()
]
