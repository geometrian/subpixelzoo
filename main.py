import os
import subprocess
import sys

#"pip install PyOpenGL"
import OpenGL.GL as GL

#"pip install pygame-ce"
with open( os.devnull, "w" ) as f:
	oldstdout=sys.stdout; sys.stdout=f; import pygame; sys.stdout=oldstdout

#"pip install scipy"
import scipy.ndimage

import screen_geom



if sys.platform in ( "win32", "win64" ):
	os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.display.init()
pygame.font.init()



PATH_LIBWEBP:str|None = "D:/tools/image processing/convert webp/libwebp-1.2.0-windows-x64/"

RES = 1024
BLUR = 8

MSAA = 16

BLUR_PAD = 4*BLUR



icon=pygame.Surface((32,32)); icon.set_colorkey((0,0,0)); pygame.display.set_icon(icon)
pygame.display.set_caption("Subpixel Generator")

pygame.display.gl_set_attribute( pygame.GL_MULTISAMPLEBUFFERS, int(bool(MSAA)) )
pygame.display.gl_set_attribute( pygame.GL_MULTISAMPLESAMPLES, MSAA            )

pygame.display.gl_set_attribute( pygame.GL_FRAMEBUFFER_SRGB_CAPABLE, 1 )

pygame.display.set_mode( (RES+2*BLUR_PAD,RES+2*BLUR_PAD), pygame.OPENGL|pygame.DOUBLEBUF )



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

	draw( ind, True,False,False )
	surf_geom = get_screenshot(False)
	draw( ind, False,True,False )
	surf_grid = get_screenshot(False)

	arr = pygame.surfarray.array3d(surf_geom)
	arr = scipy.ndimage.gaussian_filter( arr, sigma=(BLUR,BLUR,0), order=0, mode="wrap" )
	surf_geom = pygame.surfarray.make_surface(arr)

	surf_grid.set_colorkey((0,0,0))

	surf_geom.blit( surf_grid, (0,0) ) #Re-use `surf_geom` for the final output
	surf_geom = surf_geom.subsurface( BLUR_PAD,BLUR_PAD, RES,RES )
	surf_sm = pygame.transform.smoothscale(surf_geom,(128,128))

	PATH_PNG    = f"output/{geom.name}.png"
	PATH_PNG_SM = f"output/{geom.name}_sm.png"
	pygame.image.save( surf_geom, PATH_PNG    )
	pygame.image.save( surf_sm  , PATH_PNG_SM )

	if PATH_LIBWEBP == None: return
	PATH_CWEBP:str|None = PATH_LIBWEBP + "bin/cwebp.exe"

	PATH_WEBP    = f"output/{geom.name}.webp"
	PATH_WEBP_SM = f"output/{geom.name}_sm.webp"

	for path_in, path_out in ( (PATH_PNG,PATH_WEBP), (PATH_PNG_SM,PATH_WEBP_SM) ):
		cmd = [ PATH_CWEBP, "-q","80", "-m 6", "\""+path_in+"\"", "-o","\""+path_out+"\"" ]
		cmdstr = " ".join(cmd)
		subprocess.Popen( cmdstr, stdout=subprocess.PIPE,stderr=subprocess.PIPE )

def save_all():
	for k in range( len(geoms) ):
		save(k)
	print("Complete!")

def draw( ind:int, with_geom=True,with_grid=True,with_drawbox=True ):
	geom = geoms[ind]

	GL.glViewport( 0,0, RES+2*BLUR_PAD,RES+2*BLUR_PAD )

	GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )

	GL.glMatrixMode(GL.GL_PROJECTION)
	GL.glLoadIdentity()
	sc = geom.view_scale
	units_per_px = sc / RES
	lo = -BLUR_PAD * units_per_px
	hi = ( RES + 2*BLUR_PAD ) * units_per_px
	GL.glOrtho( lo,hi, hi,lo, -1.0,1.0 )

	GL.glMatrixMode(GL.GL_MODELVIEW)
	GL.glLoadIdentity()

	if with_geom:
		geom.draw()

	if with_grid:
		geom.draw_grid(8.0)

	if with_drawbox:
		GL.glLineWidth(1.0)
		GL.glColor3f( 1.0, 1.0, 0.0 )
		GL.glBegin(GL.GL_LINE_LOOP)
		GL.glVertex2f( 0.0, 0.0 )
		GL.glVertex2f( sc , 0.0 )
		GL.glVertex2f( sc , sc  )
		GL.glVertex2f( 0.0, sc  )
		GL.glEnd()

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
