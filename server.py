import pygame

# Para escolhar o sentido inicial dos objetos que se movem
import random

# # To use math.ceil
# import math

# Para manipulação de imagem
from PIL import Image
import numpy as np
# from astar import AStar

#Para leitura paralela do teclado
import threading

# #Determine if the neighboors are visible from a arbitrary point
# def visible(tmp, x, y, scale):
# 	global img_np

# 	img_x_size, img_y_size, img_z_size = img_np.shape

# 	x = x * scale
# 	y = y * scale
# 	next_x = x + scale;
# 	next_y = y + scale;
# 	right_visible = True
# 	down_visible = True
# 	tmp_y = y
# 	if next_x >= img_x_size:
# 		next_x = img_x_size - 1
# 	if next_y >= img_y_size:
# 		next_y = img_y_size - 1	

# 	#print("NP x:", x, " y:", y, " valor:", img_np[x][y])

# 	while (tmp_y <= next_y):
# 		# Se encontrou uma parede na direita então o vizinho não é visível
# 		if np.array_equal(img_np[x][tmp_y], color_black):
# 			right_visible = False
# 			break
# 		tmp_y = tmp_y + 1
# 		#print("tmp y ", tmp_y)

# 	tmp_x = x
# 	while (tmp_x <= next_x):
# 		# Se encontrou uma parede abaixo então o vizinho não é visível
# 		if np.array_equal(img_np[tmp_x][y], color_black):
# 			down_visible = False
# 			break
# 		tmp_x = tmp_x + 1

	
# 	#if right_visible == False or down_visible == False:
# 	#	print("R IV, D IV", right_visible, down_visible)
	
# 	return down_visible, right_visible

# #Generate and return a minimap create from original map
# def generate_minimap(img_np, scale):
# 	img_x_size, img_y_size, img_z_size = img_np.shape

# 	# Minimap tem tamanho dobrado pois é necessário salvar a informação se os
# 	# pilares conseguem ver-se mutuamente
# 	minimap_x_data = math.ceil(img_x_size/scale)
# 	minimap_x_size = minimap_x_data * 2
# 	minimap_y_data = math.ceil(img_y_size/scale)
# 	minimap_y_size = minimap_y_data * 2

# 	# Cria uma matriz de amostragem
# 	minimap = np.ones((minimap_x_size, minimap_y_size, img_z_size))

# 	light_grey = (150, 150, 150)
# 	dark_grey = (50, 50, 50)

# 	x = 0
# 	y = 0		
# 	while x < minimap_x_data:
# 		while y < minimap_y_data:
# 			#print("X, y", x, y, x*scale, y*scale, minimap_x_size, minimap_y_size)
# 			minimap[x*2][y*2] = img_np[x*scale][y*scale]
# 			#print("Color minimap", minimap[x*2][y*2])
# 			right, down = visible(img_np, x, y, scale)
# 			if right:
# 				minimap[(x*2)+1][y*2] = np.array(light_grey)
# 			else:
# 				minimap[(x*2)+1][y*2] = np.array(dark_grey)
# 			if down:
# 				minimap[x*2][(y*2)+1] = np.array(light_grey)
# 			else:
# 				minimap[x*2][(y*2)+1] = np.array(dark_grey)

# 			minimap[(x*2)+1][(y*2)+1] = np.array(color_black)
# 			y = y + 1
# 		x = x + 1
# 		y = 0

# 	return minimap

# def draw_line(point1, point2):
# 	global screen, surf, scale

# 	x1,y1 = point1
# 	x2,y2 = point2

# 	print("Desenhando reta de ", point1, " até ", point2)
# 	pygame.draw.line(screen, 'red', (x1*scale, y1*scale), (x2*scale, y2*scale), width = 3)
# 	#screen.blit(surf, (0, 0))


# def draw_minimap_path(minimap_path):
# 	global scale

# 	resumed_path = []

# 	old_x = False
# 	old_y = False
# 	previous_direction = False

# 	for point in minimap_path:
# 		# Se é a primeira vez no loop só salva os valores pra próxima iteração
# 		if old_x == False:
# 			old_x, old_y = point
# 			continue
# 		else:
# 			# Se já não é a primeira vez então testa se algum dos pontos mudou
# 			new_x, new_y = point
# 			if new_x == old_x:
# 				direction = "horizontal"
# 			else:
# 				direction = "vertical"
			
# 			if direction != previous_direction:
# 				print(old_x, old_y)
# 				resumed_path.append((old_x*scale, old_y*scale))
			
# 			old_x, old_y = new_x, new_y
# 			previous_direction = direction


# 	last_point = minimap_path[-1]
# 	x_last_point, y_last_point = last_point

# 	resumed_path.append((x_last_point*scale, y_last_point*scale))
	
# 	if debug_level == 2:
# 		print(resumed_path)

# 	pygame.draw.lines(screen, 'red', False, resumed_path, width = 3)
	
# 	return resumed_path

# def move_to_position(next_position):
# 	global x,y
	
# 	delta = 5

# 	next_x, next_y = next_position

# 	# Descubre se o movimento até a próxima posição é na horizontal ou na vertical	
# 	if x == next_x:
# 		delta_x = 0
# 		if y > next_y:
# 			delta_y = -delta
# 		else:
# 			delta_y = delta
# 	else:
# 		delta_y = 0
# 		if x > next_x:
# 			delta_x = -delta
# 		else:
# 			delta_x = delta
		
		
	
# 	while((x,y) != next_position):
# 		pygame.time.wait(500)
		
# 		reset_background()
# #		draw_square(x, y, color_white)
# 		x = x + delta_x
# 		y = y + delta_y
# 		draw_red_square(x, y)

# def reset_background():
# 	global img_np, start_background
# 	img_np = np.copy(start_background)

# def follow_path(minimap_path):
# 	for position in minimap_path:
# 		move_to_position(position)

def check_colision(x, y):

	# Testa limites da tela
	if x < 0 or y < 0 or x > max_screen_size or y > max_screen_size:
		return True

	# Testa se o fundo é branco (ou seja, não tem nada ali)
	if np.array_equal(img_np[x][y], color_white):
		return False
	else:
		print(img_np[x][y])
		print(color_white)
		return True

class DynamicObject:
	def __init__(self, position, direction):
		self.position = position
		self.direction = direction

		if direction == 'vertical':
			senses = ['up', 'down']
		else:
			senses = ['left', 'right']

		self.sense = random.choice(senses)

	def step(self):

		step_size = int(size/2)

		old_x, old_y = self.position
		if self.sense == 'up':
			new_x, new_y = old_x + step_size, old_y
		elif self.sense == 'down':
			new_x, new_y = old_x - step_size, old_y
		elif self.sense == 'left':
			new_x, new_y = old_x, old_y + step_size
		else:
			# right
			new_x, new_y = old_x, old_y - step_size

		# Testa se já existe um objeto na nova posição
		test_colision = check_colision(new_x, new_y)

		if test_colision == True:
			print("Test colision true")
			if self.sense == 'up':
				self.sense = 'down'
			elif self.sense == 'down':
				self.sense = 'up'
			elif self.sense == 'left':
				self.sense = 'right'
			else:
				# sense era right
				self.sense = 'left'
		else:
			self.position = new_x, new_y

			# Apaga desenho antigo
			draw_square(old_x, old_y, color_white)

			# Faz novo desenho
			draw_square(new_x, new_y, color_black)





def update_dyn_objects():
	#len_dynamic_objets = len(dynamic_objects)
	#if len_dynamic_objets > 0:
		#print(dynamic_objects)
		#print("Qtdade objetos dinâmicos ", len_dynamic_objets)
	for dyn_object in dynamic_objects:
		dyn_object.step()

def add_dynamic_object(position, direction):
	if direction == 'h':
		direction = 'horizontal'
	elif direction == 'v':
		direction = 'vertical'
	else:
		print("Direção inválida, não foi possível criar objeto")
		return False

	x, y = position[0], position[1]
	print("Adicionando objeto dinâmico, com posição inicial em: X " + str(x) + " Y " + str(y))
	
	new_dynamic_object = DynamicObject((x,y), direction)

	dynamic_objects.append(new_dynamic_object)



def add_static_object(position):
	x, y = position[0], position[1]
	print("Adicionando objeto estático em: X " + str(x) + " Y " + str(y))
	draw_square(x, y, color_black)

#Keyboard thread that read the keyboard and do something
def read_keyboard():
# 	global running, x, y, img_np
	global running

	print("Digite q para sair, s X Y posicionar um objeto estático, d X Y h|v")

	while running == True:

		keyboard_input = input(">")
		#keyboard_input = keyboard_input.strip()
		input_tokens = keyboard_input.split(' ')
		#print(keyboard_input)

		if input_tokens[0] == "q" or input_tokens[0] == "quit" or input_tokens[0] == "exit":
			running = False
		# Put a static object
		elif input_tokens[0] == 's':
			if len(input_tokens)!= 3:
				print("Digite s X Y")
			else:
				new_position= (int(input_tokens[1]), int(input_tokens[2]))
				add_static_object(new_position)
		# Put a dynamic object
		elif input_tokens[0] == 'd':
			if len(input_tokens)!= 4:
				print("Digite d X Y h|v")
			else:
				new_position= (int(input_tokens[1]), int(input_tokens[2]))
				direction = input_tokens[3]
				add_dynamic_object(new_position, direction)
		#else:
		#	print(input_tokens[0])
# 		elif keyboard_input[0] == "w":
# 			draw_red_square(x, y - size*dt)
# 		elif keyboard_input[0] == "s":
# 			draw_red_square(x, y + size*dt)
# 		elif keyboard_input[0] == "a":
# 			draw_red_square(x - size*dt, y)
# 		elif keyboard_input[0] == "d":
# 			draw_red_square(x + size*dt, y)
		
# 		elif keyboard_input[0] == "goto":
# 			x_destination = keyboard_input[1]
# 			y_destination = keyboard_input[2]
# 			x_destination = int(x_destination)
# 			y_destination = int(y_destination)
# 			#print("Moving to x:", x_destination, ", y:", y_destination)

# 			#Draw path
# 			draw_destination(x_destination, y_destination)
# 			surf = pygame.surfarray.make_surface(img_np)
# 			screen.blit(surf, (0, 0))

# 			maze = AStar(map=img_np, start=(x, y), end=(x_destination, y_destination), debug=True)
# 			if maze.solve() == True:
# 				print("Foi possível resolver")
# 				#maze_path.print_map_with_solution()
# 				maze_path = maze.get_path()
# 				print(maze_path)
# 				draw_path(maze_path)
# 			else:
# 				print("Não foi possível resolver")

# 		# Goto on minimap
# 		elif keyboard_input[0] == "gotomini":
# 			x_destination = keyboard_input[1]
# 			y_destination = keyboard_input[2]
# 			x_destination = int(x_destination)
# 			y_destination = int(y_destination)
# 			x_dest_minimaze = int(x_destination/scale)
# 			y_dest_minimaze = int(y_destination/scale)						
		
# 			x_minimap = int(x/scale)
# 			y_minimap = int(y/scale)
		
# 			maze = AStar(map=minimap, start=(x_minimap, y_minimap), end=(x_dest_minimaze, y_dest_minimaze), debug=False)
# 			if maze.solve() == True:
# 				#maze_path.print_map_with_solution()
# 				maze_path = maze.get_path()
	
# 				# Se não adicionar a posição inicial não vai desenhar a última linha até o robô pois existe uma descontinuidade na amostragem
# 				maze_path = [(x_minimap, y_minimap)] + maze_path
# 				if debug_level==2:
# 					print("Foi possível resolver. Maze path: ", maze_path)
# 				draw_path(maze_path)
# 				resumed_path = draw_minimap_path(maze_path)
				
# 				follow_path(resumed_path)
# 			else:
# 				print("Não foi possível resolver")
		
		
# 		# Teste com quadrado cyano
# 		elif keyboard_input[0] == "t":
# 			img_np[1:100,1:100] = (0, 255, 255)
# 			#img_np[:, :, 3] = (255, 255, 0)
# 			surf = pygame.surfarray.make_surface(img_np)
# 			screen.blit(surf, (0, 0))
# 		# Teste com linhas vermelhas
# 		elif keyboard_input[0] == "y":
# 			img_np[:, ::3] = (255, 0, 255)
# 			surf = pygame.surfarray.make_surface(img_np)
# 			screen.blit(surf, (0, 0))

# #Draw a possible path
# def draw_path(path_list):
# 	global img_np
# 	tmp_size = 1
# 	for node in path_list:
# 		x, y = node
# 		img_np[x:x+tmp_size, y:y+tmp_size] = (0, 255, 0)
# 	surf = pygame.surfarray.make_surface(img_np)
# 	screen.blit(surf, (0, 0))
	

def update_screen():
	surf = pygame.surfarray.make_surface(img_np)
	screen.blit(surf, (0, 0))


def draw_square(x, y, color):
	global img_np
	
	#Centraliza o robô
	x = int(x - size/2)
	y = int(y - size/2)

	img_np[x:x+size, y:y+size] = color

	update_screen()





# def draw_destination(x, y):
# 	global previous_x_destination, previous_y_destination, color_white, color_cyan
# 	#print(type(x), type(y))

# 	if previous_y_destination != -1:
# 		draw_square(previous_x_destination, previous_y_destination, color_white)

# 	draw_square(x, y, color_cyan)

# 	previous_x_destination = x
# 	previous_y_destination = y


# def draw_red_square(new_x, new_y):
# 	global x, y, color_white, color_red, img_np
	
# 	new_x = int(new_x)
# 	new_y = int(new_y)

# 	#Desenha um quadrado branco na posição anterior
# 	draw_square(x, y, color_white)
	
# 	#Redesenha o quadrado na posição atualizada
# 	if debug_level == 1:
# 		print("Drawing red square at x:", x, " y: ", y) 
# 	draw_square(new_x, new_y, color_red)

# 	surf = pygame.surfarray.make_surface(img_np)
# 	screen.blit(surf, (0, 0))

# 	#Atualiza as variáveis globais de posição
# 	x = new_x
# 	y = new_y

# # 0: none, 1: minimal, 2: maximal
# debug_level = 1

# Define que o programa pode começar a executar
running = True
dt = 0

# Tamanho padrão dos objetos
size = 30

# Tamanho da tela
max_screen_size = 500

# Configura algumas cores comuns
color_red = (255, 0, 0)

# Fundo
color_white = (255, 255, 255)
color_cyan = (0, 255, 255)

# Obstáculos móveis
color_black = (0, 0, 0)

# pygame setup
pygame.init()
screen = pygame.display.set_mode((max_screen_size, max_screen_size))
clock = pygame.time.Clock()

# # Define a posição do robô na tela 
# x = int(screen.get_width() / 2)
# y = int(screen.get_height() / 2)


# # Lê o arquivo bmp e converte para numpy
img_map = Image.open("map3.bmp")
img_np = np.array(img_map)
start_background = np.copy(img_np)

#Mostra o mapa inicial
surface = pygame.surfarray.make_surface(img_np)
screen.blit(surface, (0, 0))

# #Converte to pixel array para manipulação direta
# pxarray = pygame.PixelArray(surf)

# #Faz o desenho inicial para não começar sem o quadrado
# draw_red_square(x, y)

#Inicia a thread de leitura do teclado - Faz isso separadamente para não atrapalhar o gameloop
keyboard_thread = threading.Thread(target=read_keyboard)
keyboard_thread.start()

# #Inicialmente o programa não está pausado
# paused = False

# #Indica que inicialmente a localização do destino é inválida (não desenhar sobre a posição antiga)
# previous_x_destination = -1
# previous_y_destination = -1



# # Define um conjunto com as 6 salas. Cada sala é indicada por uma cor
# # vermelho, verde, azul, ciano, amarelo e magenta
# #rooms = {(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)}
# #rooms_paths = {}
# #for room in rooms:
# #	tmp_set = rooms - {room}
# #	for tmp_room in tmp_set:
# #		print("Room ", room, ", tmp_room ", tmp_room)
# #		if room in rooms_paths and tmp_room in rooms_paths[room]:
# #			print("Já foi calculado")
# #		else:
# #			if not room in rooms_paths:
# #				rooms_paths[room] = {}
# #			if not tmp_room in rooms_paths[room]:
# #				rooms_paths[room][tmp_room] = "aaa"
# #				if not tmp_room in rooms_paths:
# #					rooms_paths[tmp_room] = {}
# #				rooms_paths[tmp_room][room] = "-a"
			
# #for tmp_room_path in rooms_paths:
# #	print("Chave ", tmp_room_path, ", valor ", rooms_paths[tmp_room_path])



# # Quanto deve ser a escala da amostragem do mapa para acelerar o A*?
# # Ex: Amostragem de 1:10 então scale=10
# scale = 20
# minimap = generate_minimap(img_np, scale)
# if debug_level == 2:
# 	print("Minimap array: ")
# 	print(minimap)
# surf = pygame.surfarray.make_surface(minimap)
# screen.blit(surf, (0, 0))

# x_minimap = int(x/scale)
# y_minimap = int(y/scale)
# print(minimap[x_minimap][y_minimap])

# print("x minimap ", x_minimap, " , y_minimap ", y_minimap)



# #print(img_np.shape, minimap.shape)
# #print(img_np[0][0], minimap[0][0])
# data = Image.fromarray(minimap.astype(np.uint8)) 
# data.save('minimap.bmp') 

# Cria uma lista, inicialmente vazia, de objetos que se movem
dynamic_objects = []

while running:
	# poll for events
	# pygame.QUIT event means the user clicked X to close your window
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
		    running = False

# 	# fill the screen with a color to wipe away anything from last frame
# #	screen.fill("green")

# 	#position = pygame.Vector2(x, y)

	update_dyn_objects()
	
 	# flip() the display to put your work on screen
	pygame.display.flip()

	# limits FPS to 60
	# dt is delta time in seconds since last frame, used for framerate-
	# independent physics.
	dt = clock.tick(10) / 1000


# Encerra a thread de leitura do teclado
keyboard_thread.join()

# #print(img_np)

# Encerra o programa
pygame.quit()

