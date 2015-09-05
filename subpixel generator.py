import pygame
from pygame.locals import *
import sys, os, traceback
from math import *
if sys.platform in ["win32","win64"]: os.environ["SDL_VIDEO_CENTERED"]="1"
pygame.display.init()
pygame.font.init()

screen_size = [800,600]
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("Subpixel Generator")
surface = pygame.display.set_mode(screen_size)

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
CYAN = (0,255,255)
WHITE = (255,255,255)

pixel_size = 64
pixel_count = 4

half = 0.5 * pixel_size
third = 1.0/3.0 * pixel_size
quarter = 0.25 * pixel_size
fifth = 1.0/5.0 * pixel_size
sixth = 1.0/6.0 * pixel_size
one = float(pixel_size)

def rndint(num):
    return int(round(num))
def rndpt(pt,bias=(0,0)):
    return (rndint(pt[0]+bias[0]),rndint(pt[1]+bias[1]))

def get_blurred(surf):
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
class SubPixelCapsule(SubPixelBase):
    def __init__(self, color, p0,p1,radius):
        SubPixelBase.__init__(self, color)
        self.p0 = p0
        self.p1 = p1
        self.radius = rndint(radius*pixel_size)
    def draw(self, surf):
        pygame.draw.line(surf, self.color, rndpt(self.p0,[-1,-1]),rndpt(self.p1,[-1,-1]), 2*self.radius)
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
    def draw(self, surf):
        for s in self.subpixels: s.draw(surf)
    def save(self, surf):
        pygame.image.save(surf, self.name+".png")
class PixelSquareBase(PixelBase):
    def __init__(self, pattern_w,pattern_h, name):
        PixelBase.__init__(self, pattern_w,pattern_h, "square_"+name)
    def draw(self, surf):
        PixelBase.draw(self,surf)
    def draw_outlines(self, surf):
        for j in range(self.pattern_h):
            for i in range(self.pattern_w):
                pygame.draw.rect(surf, (255,0,0), (i*pixel_size,j*pixel_size,pixel_size,pixel_size), 1)

#Pixel Geometries
class PixelSquareBasic(PixelSquareBase): #No example
    def __init__(self):
        PixelSquareBase.__init__(self, 1,1, "basic")
        self.subpixels.append( SubPixelBox(WHITE, (half,half),half) )
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
class PixelSquareAltRGB(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,2, "altRBG")
        self.subpixels.append( SubPixelCapsule(RED,   (  sixth,    fifth),(  sixth,    one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (   half,    fifth),(   half,    one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (5*sixth,    fifth),(5*sixth,    one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (  sixth,one+fifth),(  sixth,one+one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (   half,one+fifth),(   half,one+one-fifth), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (5*sixth,one+fifth),(5*sixth,one+one-fifth), 0.12) )
#TODO: VRGB, VBGR
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
class PixelSquareAltBGBR(PixelSquareBase):
    def __init__(self):
        PixelSquareBase.__init__(self, 1,2, "altBGBR")
        self.subpixels.append( SubPixelCapsule(BLUE,  (    sixth,          sixth),(    sixth,    one-  sixth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (     half,        quarter),(  5*sixth,        quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (     half,    one-quarter),(  5*sixth,    one-quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(BLUE,  (one-sixth,one+      sixth),(one-sixth,one+one-  sixth), 0.12) )
        self.subpixels.append( SubPixelCapsule(GREEN, (    sixth,one+    quarter),(     half,one+    quarter), 0.12) )
        self.subpixels.append( SubPixelCapsule(RED,   (    sixth,one+one-quarter),(     half,one+one-quarter), 0.12) )
#TODO: PixelsSquarePenTileRGBW
class PixelsSquarePenTileAltRGBW(PixelSquareBase): #TODO: refine
    #Samsung Galaxy Camera
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
#TODO: PenTileRGBG
    #Google Nexus One
    #Samsung Galaxy S3
#TODO: RotTris
#TODO: DiamondRGGB
#TODO: Bayer filters
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

def gen(pixel_set, blur=True):
    pixel_surf0 = pygame.Surface(( pixel_size*pixel_set.pattern_w, pixel_size*pixel_set.pattern_h ))
    pixel_set.draw(pixel_surf0)
    if blur: pixel_surf0=get_blurred(pixel_surf0)
    pixel_surf1 = pixel_surf0.copy()
    pixel_set.draw_outlines(pixel_surf1)

    screen_square = pygame.Surface((pixel_count*pixel_size,pixel_count*pixel_size))
    for j in range(pixel_count):
        for i in range(pixel_count):
            screen_square.blit([pixel_surf0,pixel_surf1][i==0 and j==0],(i*pixel_size*pixel_set.pattern_w,j*pixel_size*pixel_set.pattern_h))

    return screen_square
def gen_save(pixel_set):
    screen_square = gen(pixel_set)
    pixel_set.save(screen_square)
##pixel_set = PixelSquareVRGB()
##screen_square = gen(pixel_set)
for pixel_set in [
##    PixelSquareBasic(),
##    PixelSquareRGB(),
##    PixelSquareBGR(),
##    PixelSquareVRGB(),
##    PixelSquareVBGR(),
##    PixelSquareAltRGB(),
    PixelSquareRGGB()
##    PixelSquareBGBR(),
##    PixelSquareAltBGBR(),
##    PixelsSquarePenTileRGBW(),
##    PixelSquareFuji_X_Trans(),
##    PixelSquareXO_1()
]:
    gen_save(pixel_set)

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
