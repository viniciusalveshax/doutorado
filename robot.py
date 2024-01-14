import pygame
from PIL import Image
import numpy as np

#Para leitura paralela do teclado
import threading

def read_keyboard():
	global running, x, y, img_np

	while running == True:

		keyboard_input = input("Digite um comando")
		#keyboard_input = keyboard_input.strip()
		keyboard_input = keyboard_input.split()
		#print(keyboard_input)

		if keyboard_input[0] == "q":
			running = False
		elif keyboard_input[0] == "w":
			draw_red_square(x, y - size*dt)
		elif keyboard_input[0] == "s":
			draw_red_square(x, y + size*dt)
		elif keyboard_input[0] == "a":
			draw_red_square(x - size*dt, y)
		elif keyboard_input[0] == "d":
			draw_red_square(x + size*dt, y)
		elif keyboard_input[0] == "goto":
			x_destination = keyboard_input[1]
			y_destination = keyboard_input[2]
			x_destination = int(x_destination)
			y_destination = int(y_destination)
			print("Moving to x:", x_destination, ", y:", y_destination)
			draw_destination(x_destination, y_destination)
			surf = pygame.surfarray.make_surface(img_np)
			screen.blit(surf, (0, 0))
		elif keyboard_input[0] == "t":
			img_np[1:100,1:100] = (0, 255, 255)
			#img_np[:, :, 3] = (255, 255, 0)
			surf = pygame.surfarray.make_surface(img_np)
			screen.blit(surf, (0, 0))
		elif keyboard_input[0] == "y":
			img_np[:, ::3] = (255, 0, 255)
			surf = pygame.surfarray.make_surface(img_np)
			screen.blit(surf, (0, 0))


def draw_destination(x, y):
	global size, img_np
	#print(type(x), type(y))
	img_np[x:x+size, y:y+size] = (0, 255, 255)
#	return img_np


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

# Lê o arquivo bmp e converte para numpy
img = Image.open("empty_map.bmp")
img_np = np.array(img)
print(img_np.shape)

#Mostra o objeto numpy
surf = pygame.surfarray.make_surface(img_np)
screen.blit(surf, (0, 0))

#Converte to pixel array para manipulação direta
pxarray = pygame.PixelArray(surf)


#imgsurface = pygame.image.load('empty_map.bmp')
#rgbarray = pygame.surfarray.pixels3d(surf)


#Faz o desenho inicial para não começar sem o quadrado
draw_red_square(x, y)

keyboard_thread = threading.Thread(target=read_keyboard)
keyboard_thread.start()

#Inicialmente o programa não está pausado
paused = False

while running:
	# poll for events
	# pygame.QUIT event means the user clicked X to close your window
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    running = False

	# fill the screen with a color to wipe away anything from last frame
#	screen.fill("green")

	#position = pygame.Vector2(x, y)
	
	# flip() the display to put your work on screen
	pygame.display.flip()

	# limits FPS to 60
	# dt is delta time in seconds since last frame, used for framerate-
	# independent physics.
	dt = clock.tick(10) / 1000


# Encerra a thread de leitura do teclado
keyboard_thread.join()

# Encerra o programa
pygame.quit()

