# Para mostrar a representação atual do mapa
import pygame

import random

import numpy as np

# Para monitorar o tópico com novidades vindo do master
import threading

# Para conectar no servidor sem passar pelo ROS
import socket

# Para desacelerar o tempo de simulação e para medir o tempo de execução
import time

# Bibliotecas do ROS2
import rclpy # type: ignore
from rclpy.node import Node # type: ignore
from rclpy.executors import MultiThreadedExecutor # type: ignore

from map_interfaces.srv import GetMapDims, GetMapSerial, RememberRobotData, AcceptTask, InformPosition, CheckObstacles # type: ignore
from std_msgs.msg import String # type: ignore

# Algoritmo do A*
from astar import AStar # type: ignore

#Fundo - Branco
color_white = (255, 255, 255)

#Paredes - Preto
color_black = (0, 0, 0)

#Robô - Verde
color_green = (0, 255, 0)

#Destino - Vermelho
color_red = (255, 0, 0)

#Obstáculo - Azul
color_security = (0, 0, 255)

# Tamanho padrão do "robô"
size = 30

# Cria um array vazio para depois ser usado globalmente
array2d = np.empty(1)

control = {}
my_position = (0,0)
MAX_X = 720
MAX_Y = 720

DEBUG = False

TASK_SERVER='127.0.0.1'
TASK_PORT=6666

WORLD_SERVER='127.0.0.1'
WORLD_PORT=6667

class MinimalSubscriber(Node):
	def __init__(self):
		super().__init__('minimal_subscriber')
		self.subscription = self.create_subscription(
		    String,
		    'map_info',
		    self.listener_callback,
		    10)
		self.subscription  # prevent unused variable warning

	def listener_callback(self, msg):
		global control
	
	
		self.get_logger().info('Recebi: "%s"' % msg.data)

		# Testa se é um aviso de obstáculo
		if " O " in msg.data:
			splitted_msg = msg.data.split()

			# Formato da mensagem 
			# timestamp + " O " + x + " " + y
			# x e y são as posições do obstáculo
			x_str = splitted_msg[2]
			y_str = splitted_msg[3]
			x = int(x_str)
			y = int(y_str)

			array2d = control["map"]
			
			# Testa se obstáculo já não está marcado
			if not np.array_equal(array2d[x][y], color_black):
				print("Marcando obstáculo em ", x, " ", y)
				mark_obstacle((x,y))
			else:
				print("Obstáculo já detectado em ", x, " ", y, ". Não vou fazer nada")

			# Encerra essa execução do callback
			return

		# Testa se é uma nova tarefa
		if control["available"] and ("Solicitando" in msg.data):
			splitted_msg = msg.data.split()
			# Formato da mensagem 
			# timestamp + "Tarefa " + task_id + " : Solicitando robô em X=" + x + " e Y=" + y
			task_id = int(splitted_msg[2])
			x_str = splitted_msg[7]
			y_str = splitted_msg[9]
			x = int(x_str.split("X=")[1])
			y = int(y_str.split("Y=")[1])

			# Nó para aceitar tarefa
			accept_task_client = AcceptTaskClient('node_accept_task', AcceptTask, 'accept_task')
			print("Enviando requisição para aceitar a tarefa")
			future_request = accept_task_client.send_request(task_id, control["my_name"])
			rclpy.spin_until_future_complete(accept_task_client, future_request)
			request_response = future_request.result()
	
			# Verifica se a tarefa ainda está disponível
			if request_response.response == True:
				print("Aceitei a tarefa ", task_id)
				control["destiny"] = (x,y)
				control["available"] = False
				control["first_step"] = True
			else:
				print("A tarefa ", task_id, " não estava mais disponível")

class MinimalClientAsync(Node):

	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#self.cli = self.create_client(GetMapData, 'get_map_data')
		self.cli = self.create_client(server_interface_type, topic_name)
		while not self.cli.wait_for_service(timeout_sec=1.0):
			self.get_logger().info('service not available, waiting again...')
		self.req = server_interface_type.Request()

	def send_request(self):
		#self.req.a = a
		#self.req.b = b
		return self.cli.call_async(self.req)

class ClientGetRobotData(Node):

	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#self.cli = self.create_client(GetMapData, 'get_map_data')
		self.cli = self.create_client(server_interface_type, topic_name)
		while not self.cli.wait_for_service(timeout_sec=1.0):
			self.get_logger().info('service not available, waiting again...')
		self.req = server_interface_type.Request()

	def send_request(self):
		#mac = "06:11:aa:bb:c1:d9"
		self.req.mac = "06:11:aa:bb:c1:d9"
		#self.req.a = a
		#self.req.b = b
		return self.cli.call_async(self.req)


class AcceptTaskClient(Node):
	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#self.cli = self.create_client(GetMapData, 'get_map_data')
		self.cli = self.create_client(server_interface_type, topic_name)
		while not self.cli.wait_for_service(timeout_sec=1.0):
			self.get_logger().info('service accept task not available, waiting again...')
		self.req = server_interface_type.Request()

	def send_request(self, task_id, robot_name):
		self.req.task_id = task_id
		self.req.robot_name = robot_name
		return self.cli.call_async(self.req)


class InformPositionClient(Node):
	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#self.cli = self.create_client(GetMapData, 'get_map_data')
		self.cli = self.create_client(server_interface_type, topic_name)
		while not self.cli.wait_for_service(timeout_sec=1.0):
			self.get_logger().info('service inform position not available, waiting again...')
		self.req = server_interface_type.Request()

	def send_request(self, robot_name, position):
		self.req.x_position = position[0]
		self.req.y_position = position[1]		
		self.req.robot_name = robot_name
		return self.cli.call_async(self.req)

class CheckObstaclesClient(Node):
	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#self.cli = self.create_client(GetMapData, 'get_map_data')
		self.cli = self.create_client(server_interface_type, topic_name)
		while not self.cli.wait_for_service(timeout_sec=1.0):
			self.get_logger().info('service check obstacles not available, waiting again...')
		self.req = server_interface_type.Request()

	def send_request(self, robot_name, new_position):
		self.req.x_position = new_position[0]
		self.req.y_position = new_position[1]		
		self.req.robot_name = robot_name
		return self.cli.call_async(self.req)



def draw_square(x, y, color):
	global array2d
	
	#Calcula o ponto do início do desenho
	x0 = int(x - size/2)
	y0 = int(y - size/2)
	
	# Se o quadrado estiver abaixao das dimensão da tela faz um ajuste
	if x0 < 0:
		x0 = 0
	if y0 < 0:
		y0 = 0
		
	# Calcula o ponto do final do desenho
	delta_x = x0 + size
	delta_y = y0 + size
	
	# Se o quadrado estiver acima dos valores das dimensões da tela faz um ajuste
	if delta_x > MAX_X:
		delta_x = MAX_X
	if delta_y > MAX_Y:
		delta_y = MAX_Y

	array2d[x0:delta_x, y0:delta_y] = color
	
def check_updates(control):

	rclpy.init()
	
	subscriber = MinimalSubscriber()

	rclpy.spin(subscriber)

	# Destroy the node explicitly
	# (optional - otherwise it will be done automatically
	# when the garbage collector destroys the node object)
	subscriber.destroy_node()
	rclpy.shutdown()

def draw_path(path_list):
	global array2d
	tmp_size = 1
	for node in path_list:
		x, y = node
		array2d[x:x+tmp_size, y:y+tmp_size] = (0, 255, 0)
	surf = pygame.surfarray.make_surface(array2d)
	screen.blit(surf, (0, 0))

def send_message_udp(server, port, message):

	# Definir o endereço e a porta do servidor
	server_conf = (server, port)  # 127.0.0.1 é o loopback (localhost)

	# Criar um socket UDP
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	# Codifica a mensagem em utf8
	coded_message = message.encode('utf-8')

	# Enviar a mensagem
	client_socket.sendto(coded_message, server_conf)

	# Receber uma resposta (opcional)
	data, _ = client_socket.recvfrom(1024)
	response = data.decode('utf-8')

	return response


def broadcast_obstacle(position):

	(x, y) = position

	# O = Obstacle
	message = "O " + str(x) + " " + str(y)

	response = send_message_udp(TASK_SERVER, TASK_PORT, message)

	response = int(response)

	if response == 1:
		return True
	else:
		return False



def check_for_obstacles(control):

	numero = random.randint(1, 100)  # número aleatório entre 1 e 100
	node_name = "check_obstacles_client" + str(numero)

	#exec = rclpy.get_global_executor()
	#nodes = exec.get_nodes()
	#print(nodes)

	#check_for_obstacles_client = CheckObstaclesClient(node_name, CheckObstacles, 'check_obstacles')

	#exec.add_node(check_for_obstacles_client)

	my_name = control["my_name"]
	my_position = control["my_position"]
	next_position = control["next_position"]

	if DEBUG:
		print("\nVerificando obstáculos em ", next_position)
	
	# Testa se o movimento é horizontal ou vertical
	# Se o x for igual então o movimento é vertical
	# se o x for diferente então o movimento é horizontal
	if my_position[0] == next_position[0]:
		if next_position[1] > my_position[1]:
			direction = 'down'
		else:
			direction = 'up'
	else:
		if next_position[0] > my_position[0]:
			direction = 'right'
		else:
			direction = 'left'

	if 'old_direction' in control:
		if control['old_direction'] != direction:
			control['turns'] = control['turns'] + 1
			if DEBUG:
				print("Mudanças de direção ", control['turns'])
	
	control['old_direction'] = direction

	# Definir o endereço e a porta do servidor
	server_conf = (WORLD_SERVER, WORLD_PORT)  # 127.0.0.1 é o loopback (localhost)

	# Criar um socket UDP
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	delta = int(size/2)

	(x_position, y_position) = next_position

	if direction == 'up':
		y_position = y_position - delta
	elif direction == 'down':
		y_position = y_position + delta
	elif direction == 'left:':
		x_position = x_position - delta
	elif direction == 'right':
		x_position = x_position + delta

	test_position = (x_position, y_position)

	message = my_name + ' ' + str(test_position[0]) + ' ' + str(test_position[1]) + ' ' + direction
	coded_message = message.encode('utf-8')

	# Enviar a mensagem
	client_socket.sendto(coded_message, server_conf)

	# Receber uma resposta (opcional)
	data, _ = client_socket.recvfrom(1024)
	response = data.decode('utf-8')
	
	if DEBUG:
		print(f"Check: Resposta do servidor: {response}")

	#future_request = check_for_obstacles_client.send_request(my_name, next_position)
	#rclpy.spin_until_future_complete(check_for_obstacles_client, future_request)
	#request_response = future_request.result()
	
	response = int(response)

	# Verifica a resposta
	if response == 1:
		if DEBUG:
			print("Encontrou um obstáculo em ", test_position)
		control["obstacles_found"] = True
		mark_obstacle(test_position, direction)
		broadcast_obstacle(test_position)

	else:
		if DEBUG:
			print("Sem obstáculos em ", test_position)
		control["obstacles_found"] = False


	#check_for_obstacles_client.destroy_node()



def inform_position(control):
	numero = random.randint(1, 100)  # número aleatório entre 1 e 100
	node_name = "node_robot_inform_position" + str(numero)
	#inform_position_client = InformPositionClient(node_name, InformPosition, 'inform_position')

	my_name = control["my_name"]
	my_position = control["my_position"]
	control["go_ahead"] = control["go_ahead"] + 1

	if DEBUG:
		print("Para frente ", control["go_ahead"])
	
	# Definir o endereço e a porta do servidor
	server_conf = (WORLD_SERVER, WORLD_PORT+1)  # 127.0.0.1 é o loopback (localhost)

	# Criar um socket UDP
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	message = my_name + ' ' + str(my_position[0]) + ' ' + str(my_position[1])
	coded_message = message.encode('utf-8')

	# Enviar a mensagem
	client_socket.sendto(coded_message, server_conf)

	# Receber uma resposta (opcional)
	data, _ = client_socket.recvfrom(1024)
	response = data.decode('utf-8')
	if DEBUG:
		print(f"Inform position: Resposta do servidor: {response}")

def mark_obstacle(position, direction = False):
	(x, y) = position

	if DEBUG:
		print("Marcando obstáculo no mapa na posição ", position)

	array2d = control["map"]

	delta_obstacle_x = 3
	delta_obstacle_y = 3

	if direction == False:
		delta_security_x = int(size/2) + delta_obstacle_x
		delta_security_y = int(size/2) + delta_obstacle_y
	else:
		if direction == 'left' or direction == 'right':
			delta_security_x = int(size/2)
			delta_security_y = int(size/2) + delta_obstacle_y
		else:
			delta_security_x = int(size/2) + delta_obstacle_x
			delta_security_y = int(size/2)

	array2d[x-delta_security_x:x+delta_security_x, y-delta_security_y:y+delta_security_y] = color_security

	array2d[x-delta_obstacle_x:x+delta_obstacle_x, y-delta_obstacle_y:y+delta_obstacle_y] = color_black

	#for tmp_x in range(x-delta_x, x+delta_x):
	#	for tmp_y in range(y-delta_y, y+delta_y):
	#		array2d[tmp_x:tmp_3, tmp_y-3:tmp_y+3] = obstacle_color

	control["map"] = array2d

def walk_one_step():
	maze_path = control["maze_path"]
	my_name = control["my_name"]
	my_position = control["my_position"]

	if DEBUG:
		print("Dentro de walk one step. Maze_path = ", maze_path)

	if len(maze_path) > 0:
		next_position = maze_path[0]
		control["maze_path"] = maze_path[1:]
	else:
		# Não tem mais nada para fazer
		control["available"] = True
		print("Cheguei ao meu objetivo")
		movements = control["turns"] + control["go_ahead"]
		# 2 Joules para cada movimento
		energy_usage = movements * 2
		print("Estimativa de energia para tarefa: ", energy_usage, " joules")
		return
	

	if DEBUG:
		print("Desenhando na próxima posição", next_position)

	control["next_position"] = next_position
	control["obstacles_found"] = False
	
	check_obstacles_thread = threading.Thread(target=check_for_obstacles, args=(control,))
	check_obstacles_thread.start()
	check_obstacles_thread.join()

	#check_for_obstacles(control)
	
	#check_for_obstacles_thread = threading.Thread(target=check_for_obstacles, args=(control,))
	#check_for_obstacles_thread.start()
	#check_for_obstacles_thread.join()

	#control["obstacles_found"] = True

	# Testa se encontrou algum obstáculo
	if not control["obstacles_found"]:
		draw_square(my_position[0], my_position[1], color_white)
		draw_square(next_position[0], next_position[1], color_green)

		control["my_position"] = next_position

		# Informa ao mundo a posição

		if DEBUG:
			print("Informando ao mundo a minha posição")
		
		inform_position_thread = threading.Thread(target=inform_position, args=(control,))
		inform_position_thread.start()
		inform_position_thread.join()
		
		# Remove a posição do labirinto
		#if len(maze_path) == 0:
		#	control["available"] = True
		#	print("Cheguei ao meu objetivo")
	
	else:
		control["first_step"] = True

	

# Ciclo de simulação do robô
def robot_step():
	global control, screen

	#rclpy.init()

	if control["available"] == True:
		if DEBUG:
			print("Nada pra fazer ...")
	else:
		if DEBUG:
			print("Tenho algo para fazer. Vou para:")
			print(control["destiny"])

		# Se a ordem é nova
		if control["first_step"] == True:
			# Marca o destino
			(x_destiny,y_destiny) = control["destiny"]
			screen = control["screen"]
			draw_square(x_destiny, y_destiny, color_red)
			surf = pygame.surfarray.make_surface(array2d)
			screen.blit(surf, (0, 0))
			my_position = control["my_position"]
			print("Novo plano. Minha posição:", my_position, " meu destino ", (x_destiny,y_destiny))

			time_before = time.perf_counter()

			# Planeja o caminho
			maze = AStar(map=array2d, start=my_position, end=(x_destiny, y_destiny), walls=[color_black, color_security], debug=DEBUG)
			if maze.solve() == True:
				#maze_path.print_map_with_solution()
				maze_path = maze.get_path()
				control["maze_path"] = maze_path
				if DEBUG:
					print("Foi possível resolver")
					print(maze_path)
				
				# Desenha a linha que mostra o caminho a ser percorrido
				draw_path(maze_path)

			else:
				print("Não foi possível resolver")

			time_after = time.perf_counter()
			
			if DEBUG:
				print(f"Tempo de execução: a* {time_after - time_before:.4f} segundos")
			
			control["first_step"] = False
		else:
			# Executa o que foi planejado
			if DEBUG:
				print("Já planejei. Agora vou executar")

			time_before = time.perf_counter()
			walk_one_step()
			time_after = time.perf_counter()
			
			if DEBUG:
				print(f"Tempo de execução: walk-one-step {time_after - time_before:.4f} segundos")
					
	#time.sleep(1)


def main(args=None):
	global array2d

	# pygame setup
	pygame.init()
	
	pygame.display.set_caption('Robô')
	
	# https://www.flaticon.com/free-icon/robot_3570207
	icon = pygame.image.load('/home/vinicius/projetos/github/doutorado/robot-icon.png') 
	pygame.display.set_icon(icon)

	screen = pygame.display.set_mode((720, 720))
	clock = pygame.time.Clock()
	running = True
	dt = 0
	control["available"] = True
	control['screen'] = screen

	# Inialização do ROS
	rclpy.init(args=args)

	# Executador de múltiplas threads
	#executor = MultiThreadedExecutor()

	# Nó para requisitar dados do mapa
	minimal_client = MinimalClientAsync('node_get_map_dims', GetMapDims, 'get_map_dims')
	#executor.add_node(minimal_client)

	print("Enviando requisição get_map_dims")
	future_request = minimal_client.send_request()
	rclpy.spin_until_future_complete(minimal_client, future_request)
	print("Requisição concluída. Dimensões do mapa:")
	request_response = future_request.result()
	map_dimensions = request_response.data

	print("Requisitando versão inicial do mapa")
	get_map_client = MinimalClientAsync('node_get_map', GetMapSerial, 'get_map_serial')
	future_request = get_map_client.send_request()
	rclpy.spin_until_future_complete(get_map_client, future_request)
	print("Mapa recebido.")
	request_response = future_request.result()
	#print(request_response.data)
	
	np_array = np.array(request_response.data)
	array2d = np_array.reshape(map_dimensions)
	control["map"] = array2d

	print("Requisitando informações a respeito do robô (posição e nome)")
	get_robot_data_client = ClientGetRobotData('node_get_robot_data', RememberRobotData, 'get_robot_data')
	future_request = get_robot_data_client.send_request()
	rclpy.spin_until_future_complete(get_robot_data_client, future_request)
	request_response = future_request.result()	
	print("Informações sobre o robô recebidas.")
	print(request_response)
	#my_position = (request_response.x_position, request_response.y_position)
	
	my_position = (20, 20)
	my_name = request_response.robot_name
	draw_square(my_position[0], my_position[1], color_green)
	control["go_ahead"] = 0
	control["turns"] = 0
	control["my_position"] = my_position
	control["my_name"] = my_name
	#control["rclpy"] = rclpy	
	
	print("Informando ao mundo a minha posição")
	inform_position_client = InformPositionClient('node_robot_inform_position', InformPosition, 'inform_position')
	future_request = inform_position_client.send_request(my_name, my_position)
	rclpy.spin_until_future_complete(inform_position_client, future_request)
	print("Informei a posição.")
	request_response = future_request.result()
	control["position_client"] = inform_position_client
	inform_position_client.destroy_node()
	
	rclpy.shutdown()

	bulletin_thread = threading.Thread(target=check_updates, args=(control,))
	bulletin_thread.start()

	while running:
		# poll for events
		# pygame.QUIT event means the user clicked X to close your window
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		# fill the screen with a color to wipe away anything from last frame
	#	screen.fill("green")
		surf = pygame.surfarray.make_surface(array2d)
		screen.blit(surf, (0, 0))

		time_before = time.perf_counter()

		robot_step()

		time_after = time.perf_counter()

		if DEBUG:
			print("Tempo em robot_step: ", time_after-time_before)

		pygame.time.wait(10)
		
		# flip() the display to put your work on screen
		pygame.display.flip()

		# limits FPS to 60
		# dt is delta time in seconds since last frame, used for framerate-
		# independent physics.
		dt = clock.tick(10) / 1000
		
	rclpy.shutdown()
	#TODO End thread	
	#bulletin_thread.stop()
	

if __name__ == '__main__':
	main()

