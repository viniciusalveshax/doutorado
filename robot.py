import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

x = screen.get_width() / 2
y = screen.get_height() / 2
size = 30

paused = False

while running:
	# poll for events
	# pygame.QUIT event means the user clicked X to close your window
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    running = False

	# fill the screen with a color to wipe away anything from last frame
	screen.fill("white")

	position = pygame.Vector2(x, y)

	# Draw a square
	square = pygame.Rect(x, y, size, size)
	pygame.draw.rect(screen, "red", square, 0)

	keys = pygame.key.get_pressed()

	if paused == False:
		if keys[pygame.K_w]:
			y -= size * dt
		if keys[pygame.K_s]:
			y += size * dt
		if keys[pygame.K_a]:
			x -= size * dt
		if keys[pygame.K_d]:
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
