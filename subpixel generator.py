import pygame
from pygame.locals import *
try:
    import scipy.ndimage
    with_scipy = True
except:
    print("Warning: SciPy not available!  Blurring will be very slow.")
    with_scipy = False
import sys, os, traceback
from math import *
if sys.platform in ["win32","win64"]: os.environ["SDL_VIDEO_CENTERED"]="1"
pygame.display.init()
pygame.font.init()

screen_size = [800,600]
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("Subpixel Generator")
surface = pygame.display.set_mode(screen_size)

PURE_RED = (255,0,0)
PURE_GREEN = (0,255,0)
PURE_BLUE = (0,0,255)
PURE_CYAN = (0,255,255)
PURE_YELLOW = (255,255,0)
PURE_MAGENTA = (255,0,255)
PURE_WHITE = (255,255,255)

RED = (208,25,3)
GREEN = (41,200,20)
BLUE = (0,43,208)
CYAN = (40,208,208)
YELLOW = (208,208,40)
MAGENTA = (208,40,208)
WHITE = (208,208,208)

##pixel_size = 67
pixel_size = 256
pixel_count = 4

if pixel_size == 64:
    outline_size = 1
elif pixel_size == 256:
    outline_size = 4
else:
    outline_size = 1

half = 0.5 * pixel_size
third = 1.0/3.0 * pixel_size
quarter = 0.25 * pixel_size
fifth = 1.0/5.0 * pixel_size
sixth = 1.0/6.0 * pixel_size
eighth = 0.125 * pixel_size
tenth = 1.0/10.0 * pixel_size
fifteenth = 1.0/15.0 * pixel_size
twentieth = 1.0/20.0 * pixel_size
thirtyfifth = 1.0/35.0 * pixel_size
fiftieth = 1.0/50.0 * pixel_size
one = float(pixel_size)

def rndint(num):
    return int(round(num))
def rndpt(pt,bias=(0,0)):
    return (rndint(pt[0]+bias[0]),rndint(pt[1]+bias[1]))

def get_blurred(surf):
    if with_scipy:
        s = pixel_size / 32.0
        arr = pygame.surfarray.array3d(surf)
        arr = scipy.ndimage.gaussian_filter(arr, sigma=(s,s,0), order=0, mode="wrap")
        result = pygame.surfarray.make_surface(arr)
        return result
    else:
        #*Much* slower, and probably not quite the same.

        w,h = surf.get_size()
        def mod(pt):
            if   pt[0] <0: pt[0]+=w
            elif pt[0]>=w: pt[0]-=w
            if   pt[1] <0: pt[1]+=h
            elif pt[1]>=h: pt[1]-=h
            return pt
        result = surf.copy()

        s = pixel_size / 16.0
        _nfalloff = -0.1

        _term2s = e**(_nfalloff*s*s)
        table = []
        table_size = int(s) + 2
        for j in range(table_size):
            row = []
            for i in range(table_size):
                weight = (e**(_nfalloff*i*i)-_term2s) * (e**(_nfalloff*j*j)-_term2s)
                if weight<0.0: weight=0.0
                row.append(weight)
            table.append(row)

        for j in range(h):
            for i in range(w):
                pt = [i,j]
                start = [int(pt[0]-s),  int(pt[1]-s)  ]
                end   = [int(pt[0]+s)+1,int(pt[1]+s)+1]
                sample_sum = [0.0,0.0,0.0]
                weight_sum = 0.0
                for jj in range(start[1],end[1]+1,1):
                    dy = abs(j - jj)
                    for ii in range(start[0],end[0]+1,1):
                        dx = abs(i - ii)
                        weight = table[dy][dx]
                        sample = surf.get_at(mod( [ii,jj] ))
                        sample_sum[0] += weight*sample[0]
                        sample_sum[1] += weight*sample[1]
                        sample_sum[2] += weight*sample[2]
                        weight_sum += weight
                blurred = [rndint(sample_sum[0]/weight_sum), rndint(sample_sum[1]/weight_sum), rndint(sample_sum[2]/weight_sum)]
                result.set_at((i,j),blurred)
        return result

#Subpixel types
class SubPixelBase(object):
    def __init__(self, color):
        self.color = color
class SubPixelBox(SubPixelBase):
    def __init__(self, color, center,radius):
        SubPixelBase.__init__(self, color)
        self.center = center
        self.radius = radius*pixel_size
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, [rndint(self.center[0]-self.radius),rndint(self.center[1]-self.radius),rndint(2*self.radius),rndint(2*self.radius)])
class SubPixelCircle(SubPixelBase):
    def __init__(self, color, center,radius):
        SubPixelBase.__init__(self, color)
        self.center = ( rndint(center[0]), rndint(center[1]) )
        self.radius = rndint(radius*pixel_size)
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, self.center, self.radius)
class SubPixelPoly(SubPixelBase):
    def __init__(self, color, points):
        SubPixelBase.__init__(self, color)
        self.points = points
    def draw(self, surf):
        ps = [rndpt(pt) for pt in self.points]
        pygame.draw.polygon(surf, self.color, ps)
class SubPixelCapsule(SubPixelBase):
    def __init__(self, color, p0,p1,radius, line_width_boost=1.0):
        SubPixelBase.__init__(self, color)
        self.p0 = p0
        self.p1 = p1
        self.radius = rndint(radius*pixel_size)
        self.line_width = rndint(2.0 * radius*pixel_size * line_width_boost)
    def draw(self, surf):
        pygame.draw.line(surf, self.color, rndpt(self.p0,[-1,-1]),rndpt(self.p1,[-1,-1]), self.line_width)
        pygame.draw.circle(surf, self.color, rndpt(self.p0), self.radius)
        pygame.draw.circle(surf, self.color, rndpt(self.p1), self.radius)
class SubPixelDiamond(SubPixelBase):
    def __init__(self, color, p,radius):
        SubPixelBase.__init__(self, color)
        self.p = p
        self.radius = radius*pixel_size
    def draw(self, surf):
        pygame.draw.polygon(surf, self.color, [rndpt(self.p,[-self.radius,0]),rndpt(self.p,[0,-self.radius]),rndpt(self.p,[self.radius,0]),rndpt(self.p,[0,self.radius])])

#Pixel types
class PixelBase(object):
    def __init__(self, pattern_w,pattern_h, name):
        self.subpixels = []
        self.pattern_w = pattern_w
        self.pattern_h = pattern_h
        self.name = name
        self.color_outline = PURE_CYAN
    def draw(self, surf):
        for s in self.subpixels: s.draw(surf)
    def draw_outline_rect(self, surf, rect):
        #Can't use this; thick lines leave an undrawn space at bottom right.
        #pygame.draw.rect(surf, self.color_outline, rect, outline_size)
        #Instead, do it manually.
        dx = dy = outline_size // 2 - 1
        for p0,p1 in [
            ((rect[0]-dx,     rect[1]        ),(rect[0]+rect[2]+dx,  rect[1]             )),
            ((rect[0]-dx,     rect[1]+rect[3]),(rect[0]+rect[2]+dx+1,rect[1]+rect[3]     )),
            ((rect[0],        rect[1]-dy     ),(rect[0],             rect[1]+rect[3]+dy  )),
            ((rect[0]+rect[2],rect[1]-dy     ),(rect[0]+rect[2],     rect[1]+rect[3]+dy+1))
        ]:
            pygame.draw.line(surf, self.color_outline, p0,p1, outline_size)
    def save(self, surf):
        pygame.image.save(surf, self.name+".png")
        pygame.image.save(pygame.transform.scale(surf,(128,128)), self.name+"_sm.png")
class PixelSquareBase(PixelBase):
    def __init__(self, pattern_w,pattern_h, name):
        PixelBase.__init__(self, pattern_w,pattern_h, "square_"+name)
    def draw(self, surf):
        PixelBase.draw(self,surf)
    def draw_outlines(self, surf):
        for j in range(self.pattern_h):
            for i in range(self.pattern_w):
                self.draw_outline_rect(surf, (i*pixel_size,j*pixel_size,pixel_size,pixel_size))
class PixelDiamondBase(PixelBase):
    def __init__(self, pattern_w,pattern_h, name):
        PixelBase.__init__(self, pattern_w,pattern_h, "diamond_"+name)
    def draw(self, surf):
        PixelBase.draw(self,surf)
    def draw_outlines(self, surf):
        points = [(0.0,0.5),(0.5,1.0),(1.0,0.5),(0.5,0.0)]
        points = [(rndint(x*pixel_size),rndint(y*pixel_size)) for x,y in points]
        for j in range(self.pattern_h):
            for i in range(self.pattern_w):
                pygame.draw.lines(surf, self.color_outline, True, points, outline_size)

#Pixel Geometries
class PixelSquareBasic(PixelSquareBase): #No example
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "basic")
        self.subpixels.append( SubPixelBox(WHITE, (half,half),half) )
        self.color_outline = PURE_RED
class PixelSquareRGB(PixelSquareBase): #Example size: 130
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "RGB")
        self.subpixels.append( SubPixelCapsule(RED,   (  sixth,fifth),(  sixth,one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (   half,fifth),(   half,one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (5*sixth,fifth),(5*sixth,one-fifth), 0.12) )
class PixelSquareBGR(PixelSquareBase): #Example size: 130
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "BGR")
        self.subpixels.append( SubPixelCapsule(BLUE,  (  sixth,fifth),(  sixth,one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (   half,fifth),(   half,one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (5*sixth,fifth),(5*sixth,one-fifth), 0.12) )
class PixelSquareAltRBG(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,2, "altRBG")
        self.subpixels.append( SubPixelCapsule(RED,   (  sixth,    fifth),(  sixth,    one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (   half,    fifth),(   half,    one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (5*sixth,    fifth),(5*sixth,    one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (  sixth,one+fifth),(  sixth,one+one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (   half,one+fifth),(   half,one+one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (5*sixth,one+fifth),(5*sixth,one+one-fifth), 0.12) )
class PixelSquareRGBChevron(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "chevRGB")
        radius = 0.10
        line_boost = 1.2
        dx = -sixth
        dy = eighth
        self.subpixels.append( SubPixelCapsule(RED,   (              sixth    +dx,   dy),(7*fifteenth            +dx,     half), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(RED,   (7*fifteenth            +dx, half),(              sixth    +dx,one-   dy), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(RED,   (              sixth+one+dx,   dy),(7*fifteenth        +one+dx,     half), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(RED,   (7*fifteenth        +one+dx, half),(              sixth+one+dx,one-   dy), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(GREEN, (               half    +dx,   dy),(7*fifteenth+  third    +dx,     half), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(GREEN, (7*fifteenth+  third    +dx, half),(               half    +dx,one-   dy), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (            5*sixth    +dx,   dy),(7*fifteenth+2*third    +dx,     half), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (7*fifteenth+2*third    +dx, half),(            5*sixth    +dx,one-   dy), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (            5*sixth-one+dx,   dy),(7*fifteenth+2*third-one+dx,     half), radius, line_boost) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (7*fifteenth+2*third-one+dx, half),(            5*sixth-one+dx,one-   dy), radius, line_boost) )
class PixelSquareRGBY(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "RGBY")
        self.subpixels.append( SubPixelCapsule(RED,    (  eighth,eighth),(  eighth,one-eighth), 0.09) )
        self.subpixels.append( SubPixelCapsule(GREEN,  (3*eighth,eighth),(3*eighth,one-eighth), 0.09) )
        self.subpixels.append( SubPixelCapsule(BLUE,   (5*eighth,eighth),(5*eighth,one-eighth), 0.09) )
        self.subpixels.append( SubPixelCapsule(YELLOW, (7*eighth,eighth),(7*eighth,one-eighth), 0.09) )
class PixelSquareVRGB(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "VRGB")
        self.subpixels.append( SubPixelCapsule(RED,   (fifth,  sixth),(one-fifth,  sixth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (fifth,   half),(one-fifth,   half), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (fifth,5*sixth),(one-fifth,5*sixth), 0.12) )
class PixelSquareVBGR(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "VBGR")
        self.subpixels.append( SubPixelCapsule(BLUE,  (fifth,  sixth),(one-fifth,  sixth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (fifth,   half),(one-fifth,   half), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (fifth,5*sixth),(one-fifth,5*sixth), 0.12) )
class PixelSquareRGGB(PixelSquareBase):  #Example size: 136?  #TODO: finish
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "RGGB")
        self.subpixels.append( SubPixelDiamond(RED,   (  quarter,    quarter), 0.15) )
        self.subpixels.append( SubPixelDiamond(GREEN, (3*quarter,    quarter), 0.15) )
        self.subpixels.append( SubPixelDiamond(GREEN, (  quarter,one-quarter), 0.15) )
        self.subpixels.append( SubPixelDiamond(BLUE,  (3*quarter,one-quarter), 0.15) )
class PixelSquareBGBR(PixelSquareBase): #Example size: 42
    #Samsung Galaxy Note II
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "BGBR")
        self.subpixels.append( SubPixelCapsule(BLUE,  (sixth,      sixth),(  sixth,one-  sixth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, ( half,    quarter),(5*sixth,    quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   ( half,one-quarter),(5*sixth,one-quarter), 0.12) )
class PixelSquareShiftBRBG(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 2,2, "shiftBRBG")
        for j in [0,1]:
            for i in [0,1]:
                x = i * pixel_size
                y = j * pixel_size
                self.subpixels.append( SubPixelCapsule(RED,   ( half+x,    quarter+y),(5*sixth-0.15*one+x,    quarter+y), 0.12) )
                self.subpixels.append( SubPixelCapsule(GREEN, ( half+x,one-quarter+y),(5*sixth-0.15*one+x,one-quarter+y), 0.12) )
                y += [0,0.3*one][i^j]
                self.subpixels.append( SubPixelCapsule(BLUE,  (eighth+x,eighth+y),(eighth+x,one-eighth-0.3*one+y), 0.08) )
class PixelSquareAltBGBR(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,2, "altBGBR")
        self.subpixels.append( SubPixelCapsule(BLUE,  (    sixth,          sixth),(    sixth,    one-  sixth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (     half,        quarter),(  5*sixth,        quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (     half,    one-quarter),(  5*sixth,    one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (one-sixth,one+      sixth),(one-sixth,one+one-  sixth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (    sixth,one+    quarter),(     half,one+    quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (    sixth,one+one-quarter),(     half,one+one-quarter), 0.12) )
class PixelsSquarePenTileAltRGWRGB(PixelSquareBase):
    #Samsung Galaxy Camera
    def __init__(self):
        PixelSquareBase.__init__(self, 2,2,"pentilealtRGWRGB")
        data = "RGWRGB\nRGBRGW"
        x=0; y=0; bias=-fiftieth
        for c in data:
            if c == "\n":
                x = 0
                y+=1; bias=-bias
            else:
                if   c == "R":
                    self.subpixels.append( SubPixelCapsule(RED,   ((2*x+1.0)*sixth-bias,(4*y+1)*quarter),((2*x+1.0)*sixth+bias,(4*y+3)*quarter), 0.10) )
                elif c == "G":
                    self.subpixels.append( SubPixelCapsule(GREEN, ((2*x+0.7)*sixth-bias,(4*y+1)*quarter),((2*x+0.7)*sixth+bias,(4*y+3)*quarter), 0.10) )
                elif c == "B":
                    self.subpixels.append( SubPixelCapsule(BLUE,  ((2*x+0.7)*sixth-bias,(4*y+1)*quarter),((2*x+0.7)*sixth+bias,(4*y+3)*quarter), 0.15) )
                else:
                    self.subpixels.append( SubPixelPoly(WHITE, [
                        ((2*x-0.2)*sixth-2.0*bias,(10*y+1)*tenth),
                        ((2*x+1.8)*sixth-2.0*bias,(10*y+1)*tenth),
                        ((2*x+1.8)*sixth+2.0*bias,(10*y+9)*tenth),
                        ((2*x-0.2)*sixth+2.0*bias,(10*y+9)*tenth)
                    ]) )
                x += 1
class PixelsSquarePenTileAltRGBW(PixelSquareBase): #TODO: refine
    def __init__(self):
        PixelSquareBase.__init__(self, 2,2,"pentilealtRGBW")
        self.subpixels.append( SubPixelCapsule(RED,   (      quarter,    quarter),(      quarter,    one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (    3*quarter,    quarter),(    3*quarter,    one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (one+  quarter,    quarter),(one+  quarter,    one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(WHITE, (one+3*quarter,    quarter),(one+3*quarter,    one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (      quarter,one+quarter),(      quarter,one+one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(WHITE, (    3*quarter,one+quarter),(    3*quarter,one+one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (one+  quarter,one+quarter),(one+  quarter,one+one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (one+3*quarter,one+quarter),(one+3*quarter,one+one-quarter), 0.12) )
class PixelsSquarePenTileAltRGBG(PixelSquareBase):
    #Google Nexus One
    #Samsung Galaxy S3
    #Samsung Galaxy Nexus
    def __init__(self):
        PixelSquareBase.__init__(self, 2,2,"pentilealtRGBG")
        for j in range(2):
            for i in range(2):
                if i == j:
                    self.subpixels.append( SubPixelBox(RED,  (one*i+third,one*j+half), 0.25) )
                else:
                    self.subpixels.append( SubPixelBox(BLUE, (one*i+third,one*j+half), 0.20) )
                self.subpixels.append( SubPixelCapsule(GREEN, (one*i+5*sixth,one*j+quarter),(one*i+5*sixth,one*j+one-quarter), 0.065) )
class PixelSquareBayer2Base(PixelSquareBase):
    def __init__(self, name, colors):
        PixelSquareBase.__init__(self, 1,1, "bayer_"+name)
        self.subpixels.append( SubPixelBox(colors[0], (  quarter,  quarter), 0.20) )
        self.subpixels.append( SubPixelBox(colors[1], (3*quarter,  quarter), 0.20) )
        self.subpixels.append( SubPixelBox(colors[2], (  quarter,3*quarter), 0.20) )
        self.subpixels.append( SubPixelBox(colors[3], (3*quarter,3*quarter), 0.20) )
class PixelSquareBayerGRBG(PixelSquareBayer2Base):
    def __init__(self): PixelSquareBayer2Base.__init__(self, "GRBG", [GREEN,RED,BLUE,GREEN])
class PixelSquareBayerWRBG(PixelSquareBayer2Base):
    def __init__(self): PixelSquareBayer2Base.__init__(self, "WRBG", [WHITE,RED,BLUE,GREEN])
class PixelSquareBayerCRBG(PixelSquareBayer2Base):
    def __init__(self): PixelSquareBayer2Base.__init__(self, "CRBG", [CYAN,RED,BLUE,GREEN])
class PixelSquareBayerCYGM(PixelSquareBayer2Base):
    def __init__(self): PixelSquareBayer2Base.__init__(self, "CYGM", [CYAN,YELLOW,GREEN,MAGENTA])
class PixelSquareBayerCYYM(PixelSquareBayer2Base):
    def __init__(self): PixelSquareBayer2Base.__init__(self, "CYYM", [CYAN,YELLOW,YELLOW,MAGENTA])
class PixelSquareBayer4Base(PixelSquareBase):
    def __init__(self, name, colors):
        PixelSquareBase.__init__(self, 1,1, "bayer_"+name)
        for j in range(4):
            for i in range(4):
                self.subpixels.append( SubPixelBox(colors[j][i], ((2*i+1)*eighth,(2*j+1)*eighth), 0.125*0.8) )
class PixelSquareKodakRGBW4a(PixelSquareBayer4Base):
    def __init__(self):
        PixelSquareBayer4Base.__init__(self, "kodak_RGBW_4a", [
            [WHITE,BLUE,WHITE,GREEN],
            [BLUE,WHITE,GREEN,WHITE],
            [WHITE,GREEN,WHITE,RED],
            [GREEN,WHITE,RED,WHITE]
        ])
class PixelSquareKodakRGBW4b(PixelSquareBayer4Base):
    def __init__(self):
        PixelSquareBayer4Base.__init__(self, "kodak_RGBW_4b", [
            [GREEN,WHITE,RED,WHITE],
            [GREEN,WHITE,RED,WHITE],
            [BLUE,WHITE,GREEN,WHITE],
            [BLUE,WHITE,GREEN,WHITE]
        ])
class PixelSquareKodakRGBW4c(PixelSquareBayer4Base):
    def __init__(self):
        PixelSquareBayer4Base.__init__(self, "kodak_RGBW_4c", [
            [GREEN,WHITE,RED,WHITE],
            [BLUE,WHITE,GREEN,WHITE],
            [GREEN,WHITE,RED,WHITE],
            [BLUE,WHITE,GREEN,WHITE]
        ])
class PixelSquareFuji_X_Trans(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 2,2, "bayer_fuji_xtrans")
        data = "GBGGRG\nRGRBGB\nGBGGRG\nGRGGBG\nBGBRGR\nGRGGBG"
        x=0; y=0
        for c in data:
            if c == "\n":
                x = 0
                y += 1
            else:
                if   c=="R": c=  RED
                elif c=="G": c=GREEN
                else:        c= BLUE
                self.subpixels.append( SubPixelBox(c, ((2*x+1)*sixth,(2*y+1)*sixth), 0.10) )
                x += 1
class PixelSquareFujiRGGBEXR(PixelDiamondBase):
    def __init__(self):
        PixelDiamondBase.__init__(self, 1,1, "RGGBEXR")
        self.name = "square_RGGBEXR"
        self.subpixels.append( SubPixelCircle(RED,   (  quarter,    quarter), 0.15) )
        self.subpixels.append( SubPixelCircle(GREEN, (3*quarter,    quarter), 0.15) )
        self.subpixels.append( SubPixelCircle(GREEN, (  quarter,one-quarter), 0.15) )
        self.subpixels.append( SubPixelCircle(BLUE,  (3*quarter,one-quarter), 0.15) )
##class PixelSquareFujiRGGBEXR(PixelSquareBase):
##    def __init__(self):
##        PixelSquareBase.__init__(self, 1,1, "RGGBEXR")
##        shift = quarter
##        self.subpixels.append( SubPixelCircle(RED,   (  quarter,    quarter), 0.15) )
##        self.subpixels.append( SubPixelCircle(GREEN, (3*quarter,    quarter), 0.15) )
##        self.subpixels.append( SubPixelCircle(GREEN, (  quarter,one-quarter), 0.15) )
##        self.subpixels.append( SubPixelCircle(BLUE,  (3*quarter,one-quarter), 0.15) )
##        self.subpixels.append( SubPixelCircle(RED,   (  quarter+shift,    quarter+shift), 0.15) )
##        self.subpixels.append( SubPixelCircle(GREEN, (3*quarter+shift,    quarter+shift), 0.15) )
##        self.subpixels.append( SubPixelCircle(GREEN, (  quarter+shift,one-quarter+shift), 0.15) )
##        self.subpixels.append( SubPixelCircle(BLUE,  (3*quarter+shift,one-quarter+shift), 0.15) )
    def draw_outlines(self, surf):
        self.draw_outline_rect(surf, (      0,      0,one,one))
        self.draw_outline_rect(surf, (quarter,quarter,one,one))
class PixelSquareXO_1(PixelSquareBase): #Example size: 136
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "xo-1")
        self.subpixels.append( SubPixelBox(RED,   (  sixth,  sixth), 0.10) )
        self.subpixels.append( SubPixelBox(GREEN, (   half,  sixth), 0.10) )
        self.subpixels.append( SubPixelBox(BLUE,  (5*sixth,  sixth), 0.10) )
        self.subpixels.append( SubPixelBox(GREEN, (  sixth,   half), 0.10) )
        self.subpixels.append( SubPixelBox(BLUE,  (   half,   half), 0.10) )
        self.subpixels.append( SubPixelBox(RED,   (5*sixth,   half), 0.10) )
        self.subpixels.append( SubPixelBox(BLUE,  (  sixth,5*sixth), 0.10) )
        self.subpixels.append( SubPixelBox(RED,   (   half,5*sixth), 0.10) )
        self.subpixels.append( SubPixelBox(GREEN, (5*sixth,5*sixth), 0.10) )
#TODO: RotTris
class PixelDiamondRGGB(PixelDiamondBase):
    def __init__(self):
        PixelDiamondBase.__init__(self, 1,1, "RGGB")
        self.subpixels.append( SubPixelDiamond(RED,   (     half,    quarter), 0.13) )
        self.subpixels.append( SubPixelDiamond(GREEN, (    quarter,     half), 0.09) )
        self.subpixels.append( SubPixelDiamond(GREEN, (one-quarter,     half), 0.09) )
        self.subpixels.append( SubPixelDiamond(BLUE,  (     half,one-quarter), 0.15) )

def gen(pixel_set, blur=True):
    print("Generating \""+pixel_set.name+"\"")

    pixel_surf = pygame.Surface(( pixel_size*pixel_set.pattern_w, pixel_size*pixel_set.pattern_h ))
    pixel_set.draw(pixel_surf)
    if blur:
        pixel_surf = get_blurred(pixel_surf)

    screen_square = pygame.Surface((pixel_count*pixel_size,pixel_count*pixel_size))
    if isinstance(pixel_set,PixelSquareBase):
        for j in range(pixel_count):
            for i in range(pixel_count):
                screen_square.blit(pixel_surf,(i*pixel_size*pixel_set.pattern_w,j*pixel_size*pixel_set.pattern_h))
    elif isinstance(pixel_set,PixelDiamondBase):
        for j in range(pixel_count):
            for i in range(pixel_count):
                screen_square.blit(pixel_surf,(i*pixel_size*pixel_set.pattern_w,j*pixel_size*pixel_set.pattern_h))
        shift = 0.5
        if isinstance(pixel_set,PixelSquareFujiRGGBEXR):
            shift = 0.25
        for j in range(pixel_count):
            for i in range(pixel_count):
                screen_square.blit(pixel_surf,(rndint((i+shift)*pixel_size*pixel_set.pattern_w),rndint((j+shift)*pixel_size*pixel_set.pattern_h)),special_flags=BLEND_ADD)

    pixel_set.draw_outlines(screen_square)

    return screen_square
def gen_save(pixel_set, blur=True):
    screen_square = gen(pixel_set,blur)
    print("Saving")
    pixel_set.save(screen_square)
    return screen_square

def init():
    global screen_square
    pixel_set = PixelSquareShiftBRBG()
    screen_square = gen_save(pixel_set,True)
##    for pixel_set in [
##        PixelSquareBasic(),
##        PixelSquareRGB(),
##        PixelSquareBGR(),
##        PixelSquareVRGB(),
##        PixelSquareVBGR(),
##        PixelSquareRGBChevron(),
##        PixelSquareRGBY(),
##        PixelSquareAltRBG(),
##        PixelSquareRGGB(),
##        PixelSquareBGBR(),
##        PixelSquareShiftBRBG(),
##        PixelSquareAltBGBR(),
##        PixelsSquarePenTileAltRGWRGB(),
##        PixelsSquarePenTileAltRGBW(),
##        PixelsSquarePenTileAltRGBG(),
##        PixelSquareBayerGRBG(),
##        PixelSquareBayerWRBG(),
##        PixelSquareBayerCRBG(),
##        PixelSquareBayerCYGM(),
##        PixelSquareBayerCYYM(),
##        PixelSquareKodakRGBW4a(),
##        PixelSquareKodakRGBW4b(),
##        PixelSquareKodakRGBW4c(),
##        PixelSquareFuji_X_Trans(),
##        PixelSquareFujiRGGBEXR(),
##        PixelSquareXO_1(),
##        PixelDiamondRGGB()
##    ]:
##        screen_square = gen_save(pixel_set)
##    print("Done!")

def get_input():
    keys_pressed = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_position = pygame.mouse.get_pos()
    mouse_rel = pygame.mouse.get_rel()
    for event in pygame.event.get():
        if   event.type == QUIT: return False
        elif event.type == KEYDOWN:
            if   event.key == K_ESCAPE: return False
    return True

def draw():
    surface.fill((64,64,64))
    surface.blit(screen_square,(0,0))
    pygame.display.flip()

def main():
    init()
    clock = pygame.time.Clock()
    while True:
        if not get_input(): break
        draw()
        clock.tick(60)
    pygame.quit()
if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
        pygame.quit()
        input()
