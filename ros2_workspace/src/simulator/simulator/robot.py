# Para mostrar a representação atual do mapa
import pygame

import numpy as np

# Para monitorar o tópico com novidades vindo do master
import threading

# Para desacelerar o tempo de simulação
import time

# Bibliotecas do ROS2
import rclpy
from rclpy.node import Node

from map_interfaces.srv import GetMapDims, GetMapSerial, RememberRobotData, AcceptTask #, SendMsgServer
from std_msgs.msg import String

# Algoritmo do A*
from astar import AStar

color_white = (255, 255, 255)
color_black = (0, 0, 0)
color_green = (0, 255, 0)
color_red = (255, 0, 0)

# Tamanho padrão do "robô"
size = 30

# Cria um array vazio para depois ser usado globalmente
array2d = np.empty(1)

control = {}
my_position = (0,0)
MAX_X = 720
MAX_Y = 720

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

def walk_one_step():
	maze_path = control["maze_path"]
	next_position = maze_path[0]
	print("Desenhando na próxima posição", next_position)
	my_position = control["my_position"]
	draw_square(my_position[0], my_position[1], color_white)
	draw_square(next_position[0], next_position[1], color_green)
	# Remove a posição do labirinto
	if len(maze_path) > 0:
		control["maze_path"] = maze_path[1:]
	else:
		control["available"] = True
		print("Cheguei no objetivo. Disponível para outra tarefa.")	
	pygame.time.wait(50)

# Ciclo de simulação do robô
def robot_step():
	global control, screen

	if control["available"] == True:
		print("Nada pra fazer ...")
	else:
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
			print("Minha posição:", my_position, " meu destino ", (x_destiny,y_destiny))
			# Planeja o caminho
			maze = AStar(map=array2d, start=my_position, end=(x_destiny, y_destiny), walls=[color_black], debug=False)
			if maze.solve() == True:
				print("Foi possível resolver")
				#maze_path.print_map_with_solution()
				maze_path = maze.get_path()
				control["maze_path"] = maze_path
				print(maze_path)
				draw_path(maze_path)
			else:
				print("Não foi possível resolver")

			
			
			control["first_step"] = False
		else:
			# Executa o que foi planejado
			print("Já planejei. Agora vou executar")
			walk_one_step()
					
	time.sleep(1)


def main(args=None):
	global array2d

	# pygame setup
	pygame.init()
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

	print("Requisitando informações a respeito do robô (posição e nome)")
	get_robot_data_client = ClientGetRobotData('node_get_robot_data', RememberRobotData, 'get_robot_data')
	future_request = get_robot_data_client.send_request()
	rclpy.spin_until_future_complete(get_robot_data_client, future_request)
	request_response = future_request.result()	
	print("Informações sobre o robô recebidas.")
	print(request_response)
	my_position = (request_response.x_position, request_response.y_position)
	my_name = request_response.robot_name
	draw_square(my_position[0], my_position[1], color_green)
	control["my_position"] = my_position
	control["my_name"] = my_name
	

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

		robot_step()
		
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

