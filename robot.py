import pygame
import imageio as iio

def draw_map(img_map):
	base_x = 0
	base_y = 0
	y = base_y
	for line in img_map:
		x = 0
		for pixel in line:
			square = pygame.Rect(base_x + x, y, size, size)
			pygame.draw.rect(screen, pixel, square, 0)
			x = x + 1
			#print(x, y)
		y = y + 1
				

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

img_map = iio.imread(uri="map.bmp")
#print(img_map)

draw_map(img_map)

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
	square = pygame.Rect(x, y, size, size)
	pygame.draw.rect(screen, "red", square, 0)

	keys = pygame.key.get_pressed()

	if paused == False:
		if keys[pygame.K_w]:
			square = pygame.Rect(x, y, size, size)
			pygame.draw.rect(screen, "white", square, 0)
			y -= size * dt
		if keys[pygame.K_s]:
			square = pygame.Rect(x, y, size, size)
			pygame.draw.rect(screen, "white", square, 0)
			y += size * dt
		if keys[pygame.K_a]:
			square = pygame.Rect(x, y, size, size)
			pygame.draw.rect(screen, "white", square, 0)
			x -= size * dt
		if keys[pygame.K_d]:
			square = pygame.Rect(x, y, size, size)
			pygame.draw.rect(screen, "white", square, 0)
			x += size * dt

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
