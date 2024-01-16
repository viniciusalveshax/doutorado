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

def draw_square(x, y, color):
	global img_np, size

	img_np[x:x+size, y:y+size] = color


def draw_destination(x, y):
	global previous_x_destination, previous_y_destination, color_white, color_cyan
	#print(type(x), type(y))

	if previous_y_destination != -1:
		draw_square(previous_x_destination, previous_y_destination, color_white)

	draw_square(x, y, color_cyan)

	previous_x_destination = x
	previous_y_destination = y


def draw_red_square(new_x, new_y):
	global x, y, color_white, color_red
	
	new_x = int(new_x)
	new_y = int(new_y)

	#Desenha um quadrado branco na posição anterior
	draw_square(x, y, color_white)
	
	#Redesenha o quadrado na posição atualizada
	draw_square(new_x, new_y, color_red)

	surf = pygame.surfarray.make_surface(img_np)
	screen.blit(surf, (0, 0))


	#Atualiza as variáveis globais de posição
	x = new_x
	y = new_y

# Configura algumas cores comuns
color_red = (255, 0, 0)
color_white = (255, 255, 255)
color_cyan = (0, 255, 255)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((720, 720))
clock = pygame.time.Clock()
running = True
dt = 0

# Set 'robot' position and size
x = int(screen.get_width() / 2)
y = int(screen.get_height() / 2)
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

#Faz o desenho inicial para não começar sem o quadrado
draw_red_square(x, y)

#Inicia a thread de leitura do teclado - Faz isso separadamente para não atrapalhar o gameloop
keyboard_thread = threading.Thread(target=read_keyboard)
keyboard_thread.start()

#Inicialmente o programa não está pausado
paused = False

#Indica que inicialmente a localização do destino é inválida (não desenhar sobre a posição antiga)
previous_x_destination = -1
previous_y_destination = -1

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

