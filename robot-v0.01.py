import pygame
from PIL import Image
import numpy as np

def draw_red_square(new_x, new_y):
	global x, y

	#Desenha um quadrado branco na posição anterior
	white_square = pygame.Rect(x, y, size, size)
	pygame.draw.rect(screen, "white", white_square, 0)
	
	#Redesenha o quadrado na posição atualizada
	red_square = pygame.Rect(new_x, new_y, size, size)
	pygame.draw.rect(screen, "red", red_square, 0)

	#Atualiza as variáveis globais de posição
	x = new_x
	y = new_y

# pygame setup
pygame.init()
screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Set 'robot' position and size
x = screen.get_width() / 2
y = screen.get_height() / 2
size = 30

img = Image.open("map.bmp")
img_np = np.array(img)
#print(img_np.shape)
#print(img_np.ndim)
surf = pygame.surfarray.make_surface(img_np)
screen.blit(surf, (0, 0))

draw_red_square(x, y)

paused = False

while running:
	# poll for events
	# pygame.QUIT event means the user clicked X to close your window
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    running = False

	# fill the screen with a color to wipe away anything from last frame
#	screen.fill("green")

	position = pygame.Vector2(x, y)

	# Draw a square
	#square = pygame.Rect(x, y, size, size)
	#pygame.draw.rect(screen, "red", square, 0)

	keys = pygame.key.get_pressed()

	if paused == False:
		if keys[pygame.K_w]:
			draw_red_square(x, y - size*dt)
		elif keys[pygame.K_s]:
			draw_red_square(x, y + size*dt)
		elif keys[pygame.K_a]:
			draw_red_square(x - size*dt, y)
		elif keys[pygame.K_d]:
			draw_red_square(x + size*dt, y)

	if keys[pygame.K_p]:
		if paused:
			paused = False
		else:
			paused = True
	else:
		if keys[pygame.K_q]:
			running = False   		

	# flip() the display to put your work on screen
	pygame.display.flip()

	# limits FPS to 60
	# dt is delta time in seconds since last frame, used for framerate-
	# independent physics.
	dt = clock.tick(10) / 1000

pygame.quit()
