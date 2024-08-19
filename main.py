import math
import os
import sys
import traceback

#"pip install PyOpenGL"
import OpenGL.GL as GL

#"pip install pygame-ce"
with open( os.devnull, "w" ) as f:
	oldstdout=sys.stdout; sys.stdout=f; import pygame; sys.stdout=oldstdout

#"pip install scipy"
import scipy.ndimage

import screen_geom
import subpixel as mod_subpixel



if sys.platform in ( "win32", "win64" ):
	os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()



WINDOW_RES = [ 1024, 1024 ]

MSAA = 16



icon=pygame.Surface((32,32)); icon.set_colorkey((0,0,0)); pygame.display.set_icon(icon)
pygame.display.set_caption("Subpixel Generator")

pygame.display.gl_set_attribute( pygame.GL_MULTISAMPLEBUFFERS, int(bool(MSAA)) )
pygame.display.gl_set_attribute( pygame.GL_MULTISAMPLESAMPLES, MSAA            )

pygame.display.gl_set_attribute( pygame.GL_FRAMEBUFFER_SRGB_CAPABLE, 1 )

pygame.display.set_mode( WINDOW_RES, pygame.OPENGL|pygame.DOUBLEBUF )



GL.glEnable(GL.GL_BLEND)
GL.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA )
#GL.glEnable(GL.GL_DEPTH_TEST)
#GL.glEnable(GL.GL_FRAMEBUFFER_SRGB)



geoms = screen_geom.all_geoms

geom_ind = 0
def get_input():
	global geom_ind
	for event in pygame.event.get():
		if   event.type == pygame.QUIT: return False
		elif event.type == pygame.KEYDOWN:
			if   event.key == pygame.K_ESCAPE: return False
			elif event.key == pygame.K_DOWN:
				geom_ind += 1
			elif event.key == pygame.K_UP:
				geom_ind -= 1
			elif event.key == pygame.K_s:
				#save(geom_ind)
				save_all()
	geom_ind %= len(geoms)

	return True

def get_screenshot( with_alpha:bool ):
	( x,y, w,h ) = GL.glGetIntegerv(GL.GL_VIEWPORT)
	if with_alpha:
		data:bytes = GL.glReadPixels( 0,0,w,h, GL.GL_RGBA,GL.GL_UNSIGNED_BYTE,None, bytes )
		surf = pygame.image.frombytes( data, (w,h), "RGBA", True )
	else:
		data:bytes = GL.glReadPixels( 0,0,w,h, GL.GL_RGB ,GL.GL_UNSIGNED_BYTE,None, bytes )
		surf = pygame.image.frombytes( data, (w,h), "RGB" , True )
	return surf

def save( ind:int ):
	geom = geoms[ind]

	draw( ind, True,False )
	surf_geom = get_screenshot(False)
	draw( ind, False,True )
	surf_grid = get_screenshot(False)

	s = 8.0
	arr = pygame.surfarray.array3d(surf_geom)
	arr = scipy.ndimage.gaussian_filter( arr, sigma=(s,s,0), order=0, mode="wrap" )
	surf_geom = pygame.surfarray.make_surface(arr)

	surf_grid.set_colorkey((0,0,0))

	surf_geom.blit( surf_grid, (0,0) ) #Re-use `surf_geom` for the final output
	surf_sm = pygame.transform.smoothscale(surf_geom,(128,128))

	pygame.image.save( surf_geom, f"output/{geom.name}.png"    )
	pygame.image.save( surf_sm  , f"output/{geom.name}_sm.png" )
def save_all():
	for k in range( len(geoms) ):
		save(k)
	print("Complete!")

def draw( ind:int, with_geom=True,with_grid=True ):
	geom = geoms[ind]

	GL.glViewport( 0,0, WINDOW_RES[0],WINDOW_RES[1] )

	GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )

	GL.glMatrixMode(GL.GL_PROJECTION)
	GL.glLoadIdentity()
	aspect = float(WINDOW_RES[0]) / float(WINDOW_RES[1])
	sc = geom.view_scale
	GL.glOrtho( -0.01*sc,1.01*sc*aspect, 1.01*sc,-0.01*sc, -1.0,1.0 )

	GL.glMatrixMode(GL.GL_MODELVIEW)
	GL.glLoadIdentity()

	if with_geom:
		geom.draw()

	if with_grid:
		geom.draw_grid( 1.02*sc, 8.0 )

	pygame.display.flip()

def main():
	clock = pygame.time.Clock()
	while True:
		if not get_input(): break
		draw(geom_ind)

		clock.tick()
		#print( clock.get_fps() )

	pygame.quit()

if __name__ == "__main__":
	main()
	#import cProfile; cProfile.run("main()",sort="tottime")
