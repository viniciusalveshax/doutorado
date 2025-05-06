# Para mostrar a representação atual do mapa
import pygame

import numpy as np

# Bibliotecas do ROS2
import rclpy
from rclpy.node import Node

from map_interfaces.srv import GetMapDims, GetMapSerial, RememberRobotData #, SendMsgServer

color_black = (0, 0, 0)

# Tamanho padrão do "robô"
size = 30

# Cria um array vazio para depois ser usado globalmente
array2d = np.empty(1)

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


def draw_square(x, y, color):
	global array2d
	
	#Descobre a diagonal do robô
	x0 = int(x - size/2)
	y0 = int(y - size/2)

	array2d[x0:x0+size, y0:y0+size] = color

def main(args=None):
	global array2d

	# pygame setup
	pygame.init()
	screen = pygame.display.set_mode((720, 720))
	clock = pygame.time.Clock()
	running = True
	dt = 0
	my_position = (0,0)

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
	draw_square(my_position[0], my_position[1], color_black)


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


		#position = pygame.Vector2(x, y)
		
		# flip() the display to put your work on screen
		pygame.display.flip()

		# limits FPS to 60
		# dt is delta time in seconds since last frame, used for framerate-
		# independent physics.
		dt = clock.tick(10) / 1000
	

if __name__ == '__main__':
	main()

