# Para mostrar a representação atual do mapa
import pygame

import numpy as np

# Bibliotecas do ROS2
import rclpy
from rclpy.node import Node

from map_interfaces.srv import GetMapDims, GetMapSerial #, SendMsgServer


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



def main(args=None):

	# pygame setup
	pygame.init()
	screen = pygame.display.set_mode((720, 720))
	clock = pygame.time.Clock()
	running = True
	dt = 0

	# Tamanho padrão do "robô"
	size = 30

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

