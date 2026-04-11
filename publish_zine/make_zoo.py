import os
import sys

with open( os.devnull, "w" ) as f:
	oldstdout=sys.stdout; sys.stdout=f; import pygame; sys.stdout=oldstdout



DIR_SELF = os.path.dirname(__file__)
DIR_IMGS = DIR_SELF + "/../output/"
sq   = []
tri  = []
pent = []
filt = []
for item in os.listdir(DIR_IMGS):
	if ".png" not in item:
		continue
	if "_sm" in item:
		continue

	if   item.startswith("sq_"  ): sq  .append(item)
	elif item.startswith("tri"  ): tri .append(item)
	elif item.startswith("pent_"): pent.append(item)
	elif item.startswith("filt_"): filt.append(item)
	else:
		assert False
sq.remove("sq_Basic.png")

#for arr in ( sq, tri, pent, filt ):
#	print(len(arr))
#	print(arr)

GRID_W = 7
EMPTY_LEFT = 5
EMPTY_ROWS = 7
IMG_RES = 512 // 4
PAD     =  32 // 4

grid = []
row = []
for item in sq + pent + filt + tri:
	if len(grid)<EMPTY_ROWS and row==[]:
		row = [ None ]*EMPTY_LEFT
	row.append(item)
	if len(row) == GRID_W:
		grid.append(row)
		row = []
if len(row) != 0:
	grid.append(row)

GRID = ( GRID_W, len(grid) )

BG_RES = ( GRID[0]*IMG_RES+(GRID[0]+1)*PAD, GRID[1]*IMG_RES+(GRID[1]+1)*PAD )
#surf = pygame.Surface( BG_RES, pygame.SRCALPHA )
#surf.fill(( 0,0,0, 0 ))
surf = pygame.Surface(BG_RES) #Smaller filesize
surf.fill(( 255,255,255 ))
for j,row in enumerate(grid):
	for i,item in enumerate(row):
		if item == None: continue
		x = PAD + i*( IMG_RES + PAD )
		y = PAD + j*( IMG_RES + PAD )
		img = pygame.transform.smoothscale( pygame.image.load(DIR_IMGS+item), (IMG_RES,IMG_RES) )
		surf.blit( img, (x,y) )
pygame.image.save( surf, DIR_SELF+"/background_raw.png" )
