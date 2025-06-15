
import rclpy # type: ignore
from rclpy.node import Node # type: ignore
from rclpy.executors import MultiThreadedExecutor # type: ignore

from std_msgs.msg import String # type: ignore

# Para gerar o timestamp
import time

# Para lançar a thread do teclado
import threading

# Para encontrar a posição inicial do robô
import random 

# To load image
from PIL import Image
import numpy as np

#from map_interfaces.msg import GetMapInfo
from map_interfaces.srv import GetMapData, GetMapDims, GetMapSerial, RememberRobotData, AcceptTask # type: ignore #, SendMsgServer

color_white = (255, 255, 255)

# ID da nova tarefa a ser criada
task_id = 0
# Lista de tarefas
task_list = {}

def empty_space(img_np, x, y):
	print(img_np[x][y])
	
	#TODO Melhorar esse algoritmo aqui
	# Se está próximo da borda então está só o centro
	if x < 15 or y < 15 or x > 700 or y > 700:
		if np.array_equal(img_np[x][y],color_white):
			return True
		else:
			return False
	# se não está tão próximo das bordas testa as diagonais também
	else:
		if np.array_equal(img_np[x][y],color_white) and np.array_equal(img_np[x][y],img_np[x-15][y])  and np.array_equal(img_np[x][y],img_np[x+15][y])  and np.array_equal(img_np[x][y],img_np[x][y-15])  and np.array_equal(img_np[x][y],img_np[x][y+15]):
			return True
		else:
			return False

def find_space_to_place_robot():
	print("Entrei na função que procura um lugar vazio")
	
	# Lê o arquivo bmp e converte para numpy
	img = Image.open("/home/vinicius/s/doutorado/map2.bmp")
	img_np = np.array(img)

	test_x = random.randint(0, 720)
	test_y = random.randint(0, 720)
	while empty_space(img_np, test_x, test_y) == False:
		test_x = random.randint(0, 720)
		test_y = random.randint(0, 720)
		print("Novo teste de posição ...")

	return (test_x, test_y)		

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


class RobotDataService(MinimalService):
	def callback_method(self, request, response):
		self.get_logger().info('Solicitando informações de robo')

		mac_address = request.mac

		print('O robô com mac ', mac_address, 'está pedindo informações')

		(x, y) = find_space_to_place_robot()
		
		available_names = ["Wall_E", "Johnny_V", "ED209"]
		#TODO Prevent name reutilization
		choosed_name = random.choice(available_names)	

		response.x_position = x
		response.y_position = y 
		response.robot_name = choosed_name
	
		
		print("Enviando as informações do robô. Nome ", choosed_name, " x: ", x, " y: ", y)

		return response


class AcceptTaskService(MinimalService):
	def callback_method(self, request, response):
		global task_list
		self.get_logger().info('Recebendo confirmação de aceitação de tarefa')

		robot_name = request.robot_name
		task_id = request.task_id

		print('O robô ', robot_name, ' quer aceitar a tarefa ', task_id)
		
		# Testa se a tarefa está disponível
		if task_list[task_id]["available"] == True:
			# Caso sim confirma ao robô que ele pode começar,
			# marca a tarefa como indisponível e 
			# armazena o robô responsável pela tarefa
			response.response = True
			task_list[task_id]["available"] = False
			task_list[task_id]["robot_name"] = robot_name
			print(task_list[task_id])
		else:
			# Caso não informa ao robô que a tarefa não está mais disponível
			response.response = False
			print("Respondendo ao robô ", robot_name, " que a tarefa ", task_id, " não está mais disponível")
		
		print("Enviando a informação sobre confirmação da tarefa")

		#TODO Informar que a tarefa não está mais disponível

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
		
		provide_robot_data = RobotDataService('node_get_robot_data', RememberRobotData, 'get_robot_data')
		executor.add_node(provide_robot_data)

		provide_accept_task_service = AcceptTaskService('node_accept_task', AcceptTask, 'accept_task')
		executor.add_node(provide_accept_task_service)


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
			provide_map_dims_service.destroy_node()
			provide_map_serial.destroy_node()
			provide_robot_data.destroy_node()
			provide_accept_task_service.destroy_node()

	finally:
		# Destroi o nodo publicador
		print("Encerrando a execução do ROS")
		rclpy.shutdown()


def publish_bulletin(publisher, content = ''):
	#global bulletin_publisher

	i = int(time.time())

	msg = String()

	#map_info_msg.timestamp = '%d' % i
	msg.data = str(i) + ' ' + content

	#bulletin_publisher.publish(msg)
	publisher.publish(msg)

	print("Publiquei: ", msg)

def goto(x, y):
	global bulletin_publisher, task_id

	# Adiciona a tarefa na lista de tarefas
	task_list[task_id] = {'destiny': (x, y), 'available': True}
	print("Nova tarefa ", task_list[task_id])

	# Publica a tarefa nova
	content = "Tarefa " + str(task_id) + " : Solicitando robô em X=" + x + " e Y=" + y
	publish_bulletin(bulletin_publisher, content)
	
	task_id = task_id + 1
	

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


