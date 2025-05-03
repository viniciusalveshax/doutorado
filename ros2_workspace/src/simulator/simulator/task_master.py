
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from std_msgs.msg import String

# Para gerar o timestamp
import time


# Para lançar a thread do teclado
import threading

# To load image
from PIL import Image
import numpy as np

#from map_interfaces.msg import GetMapInfo
from map_interfaces.srv import GetMapData, GetMapDims, GetMapSerial #, SendMsgServer


class MinimalPublisher(Node):

	def __init__(self):
		super().__init__('minimal_publisher')
		#self.publisher_ = self.create_publisher(GetMapInfo, '/map_info', 10)
		self.publisher_ = self.create_publisher(String, '/bulletin_board', 10)
		self.i = 0

#	def timer_callback(self):
#		msg = GetMapInfo()
#		msg.timestamp = 'Hello World: %d' % self.i
#		msg.height = 100
#		msg.width = 100
#		self.publisher_.publish(msg)
#		self.get_logger().info('Publishing: "%s"' % msg.timestamp)
#		self.i += 1
        
class MinimalService(Node):
	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#        self.srv = self.create_service(GetMapData, 'get_map_data', self.get_map_data_callback)
		self.srv = self.create_service(server_interface_type, topic_name, self.callback_method)

class MapService(MinimalService):
	def callback_method(self, request, response):
		#global map
		#self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))
		self.get_logger().info('Incoming request')

		response.data = ['Test string'] #map.content() 

		print("Vou retornar")

		return response
		
class MapDimsService(MinimalService):
	def callback_method(self, request, response):
		#global map
		#self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))
		self.get_logger().info('Map Dims Incoming request')

		response.data = (720, 720, 3) #map.content() 

		print("Respondi as dimensões do mapa")

		return response

class MapSerialService(MinimalService):
	def callback_method(self, request, response):
		global serialized_map
		#self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))
		self.get_logger().info('Map Serial Incoming request 720')

		# Lê o arquivo bmp e converte para numpy
		img = Image.open("/home/vinicius/s/doutorado/map2.bmp")
		img_np = np.array(img)
		start_background = np.copy(img_np)
		serialized_map = img_np.reshape(-1)
		
		# Aparentemente não é possível enviar um array numpy então preciso converter para python
		# TODO Verificar se img já não é a mesma informação
		response.data = serialized_map.tolist() #map.content() 
		#response.data = [1, 2, 3, 4]

		print("Enviei a versão atual do mapa")

		return response




def start_ros_nodes():
	global rclpy
	
	print("Iniciando criação dos nós ROS")

	node = rclpy.create_node('task_master')
	bulletin_publisher = node.create_publisher(String, '/map_info', 10)

	#rclpy.spin(node)
	
	keyboard_thread = threading.Thread(target=read_keyboard, args=(bulletin_publisher, ))
	keyboard_thread.start()
	
	print(type(node))
	print(type(bulletin_publisher))
	#publish_bulletin(bulletin_publisher, "Teste")

	# Trecho do executador adaptado a partir daqui
	# https://robotics.stackexchange.com/questions/105877/node-keeps-crashing-due-to-valueerror-generator-already-executing
	try:
		executor = MultiThreadedExecutor()

		executor.add_node(node)
		
		provide_map_dims_service = MapDimsService('node_provide_data_dims', GetMapDims, 'get_map_dims')
		executor.add_node(provide_map_dims_service)

		provide_map_serial = MapSerialService('node_get_map_serial', GetMapSerial, 'get_map_serial')
		executor.add_node(provide_map_serial)

#		receive_msg_service = ReceiveMsgService('node_receive_msg', SendMsgServer, 'send_msg_server')
#		executor.add_node(receive_msg_service)

		try:
			executor.spin()
		except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
			executor.shutdown()
			#node_publisher.destroy_node()
#			receive_msg_service.destroy_node()
#			get_map_service.destroy_node()
		finally:
			executor.shutdown()
			#node_publisher.destroy_node()
#			receive_msg_service.destroy_node()
			node.destroy_node()
			get_map_serial.destroy_node()

	finally:
		# Destroi o nodo publicador
		print("Encerrando a execução do ROS")
		rclpy.shutdown()


def publish_bulletin(publisher, content = ''):
	#global bulletin_publisher

	i = int(time.time())

	msg = String()

	#map_info_msg.timestamp = '%d' % i
	msg.data = str(i) + content

	#bulletin_publisher.publish(msg)
	publisher.publish(msg)

	print("Publiquei: ", msg)

def goto(x, y):
	global bulletin_publisher

	content = "Solicitando robô em X=" + x + " e Y=" + y
	publish_bulletin(bulletin_publisher, content)

def read_keyboard(publisher):
	global bulletin_publisher

	bulletin_publisher = publisher
	# Inicia os serviços e cria os tópicos
	#start_ros_nodes()

	print("Iniciando leitura do teclado")

	input_tokens = ['']
	while input_tokens[0] != 'quit':
		print("Digite quit para sair")
		print("Digite goto X Y para mandar um robô para algum destino")
		keyboard_input = input("Digite um comando")
		input_tokens = keyboard_input.split(' ')
		if input_tokens[0] == "goto":
			goto(input_tokens[1], input_tokens[2])


def main(args=None):
	rclpy.init(args=args)

	start_ros_nodes()

	# Quando a thread do teclado encerrar encerra o ROS também
	rclpy.shutdown()        


