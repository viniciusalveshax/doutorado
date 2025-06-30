import pygame

# Para escolhar o sentido inicial dos objetos que se movem
import random

# # To use math.ceil
# import math

# Para criar o serviço que verifica obstáculos
import socket

# Para manipulação de imagem
from PIL import Image
import numpy as np
# from astar import AStar

#Para leitura paralela do teclado
import threading

import rclpy # type: ignore
from rclpy.node import Node # type: ignore
from rclpy.executors import MultiThreadedExecutor # type: ignore

from std_msgs.msg import String # type: ignore

from map_interfaces.srv import InformPosition, CheckObstacles # type: ignore

# Cria uma lista, inicialmente vazia, de objetos que se movem
dynamic_objects = []

static_objects = []

robot_objects = {}

# Configura algumas cores comuns

# Fundo
color_white = (255, 255, 255)

# Robôs
color_yellow = (255, 255, 0)
color_cyan = (0, 255, 255)
color_magent = (255, 0, 255)

# Área de segurança
color_security = (0, 0, 255)

# Obstáculos fixos
color_black = (0, 0, 0)

robot_colors = {
	"Wall_E": color_yellow,
	"Johnny_V": color_cyan,
	"ED209": color_magent
}

dt = 0

# Tamanho padrão dos objetos
size = 30
obstacle_size = 10

# Tamanho da tela
max_screen_size = 720

img_np = np.empty((2, 2))

screen = pygame.display.set_mode((max_screen_size, max_screen_size))

DEBUG=False

# Informação para a conexão UDP
SERVER='127.0.0.1'
PORT=6667

class MinimalService(Node):
	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#        self.srv = self.create_service(GetMapData, 'get_map_data', self.get_map_data_callback)
		self.srv = self.create_service(server_interface_type, topic_name, self.callback_method)

class CheckObstaclesService(MinimalService):
	def callback_method(self, request, response):
		global robot_objects

		if DEBUG:
			self.get_logger().info('Robô verificando obstáculos')

		robot_name = request.robot_name
		x_position = request.x_position
		y_position = request.y_position

		# Testa se o fundo é branco na futura posição
		# Caso sim então não tem nenhum obstáculo
		if np.array_equal(img_np[x_position][y_position], color_white):
			response.response = False
		else:
			print("Obstáculo encontrado")
			response.response = True

		return response



class InformPositionService(MinimalService):
	def callback_method(self, request, response):
		global robot_objects

		if DEBUG:
			self.get_logger().info('Robô informando posição')

		robot_name = request.robot_name
		x_position = request.x_position
		y_position = request.y_position

		# Verificar se a chave 'idade' existe
		if robot_name in robot_objects:
			if DEBUG:
				print('O robô com nome ', robot_name, ' está atualizando a sua posição: x ', x_position, ' y ', y_position)
			robot_objects[robot_name]["old_position"] = robot_objects[robot_name]["my_position"]
			robot_objects[robot_name]["my_position"] = (x_position, y_position)

		else:
			print('O robô com nome ', robot_name, ' está informando a sua posição pela 1ª vez: x ', x_position, ' y ', y_position)
			robot_objects[robot_name] = {"my_position": (x_position, y_position)}

		response.response = True

		return response


def check_colision(x, y, movement_sense):

	#print("Testando colisão x=", x, " y=", y, " sense=", movement_sense)

	# Testa limites da tela
	if x < 0 or y < 0 or x > max_screen_size or y > max_screen_size:
		return True

	# (x,y) é o ponto médio da frente do objeto, 
	# a frente do objeto é um segmento de reta, a partir do ponto médio calcule 
	# dois pontos, um pra esquerda e um pra direita
	step_size = int(size/2)

	if movement_sense == 'up':
		x_left, y_left = x - step_size, y
		x_right, y_right = x + step_size, y
	elif movement_sense == 'down':
		x_left, y_left = x + step_size, y
		x_right, y_right = x - step_size, y
	elif movement_sense == 'left':
		x_left, y_left = x, y - step_size
		x_right, y_right = x, y + step_size
	else:
		# sense = right
		x_left, y_left = x, y + step_size
		x_right, y_right = x, y - step_size

	#robot_color = robot_colors[robot_name]
		
	#print("Testando para ponto no meio ", x, y)	
	#print("Testando para ponto na esquerda ", x_left, y_left)
	#print("Testando para ponto na direita ", x_right, y_right)

	# Testa se o fundo é branco (ou seja, não tem nada ali)
	if np.array_equal(img_np[x][y], color_white) and np.array_equal(img_np[x_left][y_left], color_white) and np.array_equal(img_np[x_right][y_right], color_white):
		return False
	else:
		print(img_np[x][y], img_np[x_left][y_left], img_np[x_right][y_right])
		#print(color_white)
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

		test_size = int(size/2) + 1

		old_x, old_y = self.position
		new_x, new_y = old_x, old_y
		if self.sense == 'up':
			test_x, test_y = old_x, old_y - test_size
			new_y = new_y - 1
		elif self.sense == 'down':
			test_x, test_y = old_x, old_y + test_size
			new_y = new_y + 1
		elif self.sense == 'left':
			test_x, test_y = old_x - test_size, old_y
			new_x = new_x - 1
		else:
			# right
			test_x, test_y = old_x + test_size, old_y
			new_x = new_x + 1

		# Testa se já existe um objeto na nova posição
		test_colision = check_colision(test_x, test_y, self.sense)

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





def update_objects():
	global dynamic_objects, robot_objects
	#len_dynamic_objets = len(dynamic_objects)
	#if len_dynamic_objets > 0:
		#print(dynamic_objects)
		#print("Qtdade objetos dinâmicos ", len_dynamic_objets)
	for dyn_object in dynamic_objects:
		dyn_object.step()

	#print(robot_objects)	
	for robot_name, robot_positions in robot_objects.items():
		update_robot(robot_positions, robot_colors[robot_name])	

		
def update_robot(robot_positions, robot_color):

	#TODO Testa se já existia um robô com esse nome, caso sim apaga o desenho da posição antiga

	if DEBUG:
		print("Vou desenhar um robô em ", robot_positions)

	if "old_position" in robot_positions:
		(old_x, old_y) = robot_positions["old_position"]
		draw_square(old_x, old_y, color_white)		

	#Atualiza posição
	#robot_objects[robot_name] = (x,y)
	(new_x, new_y) = robot_positions["my_position"]
	
	#Desenha robô na posição nova
	draw_square(new_x, new_y, robot_color)
		
	#print("Posição do robô ", robot_name, " é X:", x, " e Y:", y) 

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
	
	static_objects.append((x,y))
	print("Adicionando objeto estático em: X " + str(x) + " Y " + str(y))
	draw_square(x, y, color_black, obstacle_size)

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

def update_screen():
	surf = pygame.surfarray.make_surface(img_np)
	screen.blit(surf, (0, 0))


def draw_square(x, y, color, square_size = 30):
	global img_np
	
	half_square = int(square_size/2)

	img_np[x-half_square:x+half_square, y-half_square:y+half_square] = color

	update_screen()

def start_ros_services():

	rclpy.init()

	try:

		executor = MultiThreadedExecutor()

		inform_position_service = InformPositionService('node_inform_position', InformPosition, 'inform_position')
		executor.add_node(inform_position_service)

		#check_obstacles_service = CheckObstaclesService('node_check_obstacles', CheckObstacles, 'check_obstacles')
		#executor.add_node(check_obstacles_service)

		try:
			executor.spin()
		except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
			executor.shutdown()
		finally:
			inform_position_service.destroy_node()
			#check_obstacles_service.destroy_node()
			executor.shutdown()


	finally:
		# Destroi o nodo publicador
		print("Encerrando a execução do ROS")
		rclpy.shutdown()



def inform_position_service(running, robot_objects):

	server_conf = (SERVER, PORT+1)  # '' significa que o servidor ouvirá em todas as interfaces

	# Criar um socket UDP
	socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Vincular o socket ao endereço
	socket_server.bind(server_conf)

	while running:
		data, client_address = socket_server.recvfrom(1024)  # 1024 é o tamanho máximo do buffer

		# Decodificar os dados
		message = data.decode('utf-8')

		print(message)
		robot_name, robot_x, robot_y = message.split(' ')
		x_position = int(robot_x)
		y_position = int(robot_y)

		if robot_name in robot_objects:
			if DEBUG:
				print('O robô com nome ', robot_name, ' está atualizando a sua posição: x ', x_position, ' y ', y_position)
			robot_objects[robot_name]["old_position"] = robot_objects[robot_name]["my_position"]
			robot_objects[robot_name]["my_position"] = (x_position, y_position)

		else:
			print('O robô com nome ', robot_name, ' está informando a sua posição pela 1ª vez: x ', x_position, ' y ', y_position)
			robot_objects[robot_name] = {"my_position": (x_position, y_position)}

		response = str(True)

		# Enviar uma resposta
		response = response.encode('utf-8')
		socket_server.sendto(response, client_address)


def check_obstacles_service(running, img_np):

	server_conf = (SERVER, PORT)  # '' significa que o servidor ouvirá em todas as interfaces

	# Criar um socket UDP
	socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Vincular o socket ao endereço
	socket_server.bind(server_conf)

	while running:
		data, client_address = socket_server.recvfrom(1024)  # 1024 é o tamanho máximo do buffer

		# Decodificar os dados
		message = data.decode('utf-8')

		print(message)
		robot_name, robot_x, robot_y, direction = message.split(' ')
		
		delta = int(size/2)

		x_position = int(robot_x)
		y_position = int(robot_y)

		print("Posição passada é x=", x_position, " y=", y_position, " direção é ", direction, end='')

		delta = 0
		if direction == 'up':
			y_position = y_position - delta
		elif direction == 'down':
			y_position = y_position + delta
		elif direction == 'left:':
			x_position = x_position - delta
		elif direction == 'right':
			x_position = x_position + delta

		print(". Testando em x ", x_position, " e y ", y_position, " é = ", img_np[x_position][y_position])

		robot_color = robot_colors[robot_name]

		if np.array_equal(img_np[x_position][y_position], color_white) or np.array_equal(img_np[x_position][y_position], robot_color) or  np.array_equal(img_np[x_position][y_position], color_security):
			response = str(0)
		else:
			response = str(1)
			print("Obstáculo encontrado")
		
		# Enviar uma resposta
		response = response.encode('utf-8')
		socket_server.sendto(response, client_address)


def main(args=None):
	global running, img_np

	# Define que o programa pode começar a executar
	running = True

	# pygame setup
	pygame.init()
	pygame.display.set_caption('World')

	# https://www.flaticon.com/free-icon/globe_183595
	icon = pygame.image.load('/home/vinicius/projetos/github/doutorado/world.png') 
	pygame.display.set_icon(icon)


	print(type(screen))
	
	clock = pygame.time.Clock()

	# # Define a posição do robô na tela 
	# x = int(screen.get_width() / 2)
	# y = int(screen.get_height() / 2)

	# # Lê o arquivo bmp e converte para numpy
	img_map = Image.open("/home/vinicius/s/doutorado/map2.bmp")
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
	
	ros_services_thread = threading.Thread(target=start_ros_services)
	ros_services_thread.start()

	check_obstacles_service_thread = threading.Thread(target=check_obstacles_service, args=(running, img_np))
	check_obstacles_service_thread.start()

	inform_position_service_thread = threading.Thread(target=inform_position_service, args=(running, robot_objects))
	inform_position_service_thread.start()

	while running:
		# poll for events
		# pygame.QUIT event means the user clicked X to close your window
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		update_objects()
		
	 	# flip() the display to put your work on screen
		pygame.display.flip()

		# limits FPS to 60
		# dt is delta time in seconds since last frame, used for framerate-
		# independent physics.
		dt = clock.tick(10) / 1000


	# Encerra a thread de leitura do teclado
	keyboard_thread.join()

	check_obstacles_service_thread.join()

	inform_position_service_thread.join()

	# Encerra o programa
	pygame.quit()


if __name__ == '__main__':
	main()
