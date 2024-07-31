#Base code from https://answers.ros.org/question/337870/ros2-how-do-i-publish-exactly-one-message/

from time import sleep

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

# Somente para testes iniciais
import random

# Para gerar o timestamp
import time

# Para lançar serviço
import threading

from map_interfaces.msg import GetMapInfo
from map_interfaces.srv import GetMapData, SendMsgServer

# Importa a classe que armazena o mapa
import sys
#TODO fazer isso dentro do padrão do ROS2
sys.path.append('/home/vinicius/projetos/github/doutorado/ros2_workspace')
from map import Map

class MinimalPublisher(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(GetMapInfo, '/map_info', 10)
        #timer_period = 0.5  # seconds
        #self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = GetMapInfo()
        msg.timestamp = 'Hello World: %d' % self.i
        msg.height = 100
        msg.width = 100
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.timestamp)
        self.i += 1


class MinimalService(Node):

    def __init__(self, node_name, server_interface_type, topic_name):
        super().__init__(node_name)
#        self.srv = self.create_service(GetMapData, 'get_map_data', self.get_map_data_callback)
        self.srv = self.create_service(server_interface_type, topic_name, self.callback_method)


class MapService(MinimalService):
    def callback_method(self, request, response):
        global map
        response.data = map.content()
        #self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))

        return response

class ReceiveMsgService(MinimalService):
    def callback_method(self, request, request_response):
        global map

        content = request.a
	
        print("Recebi uma mensagem. Conteúdo: ", content)
        
        # Encontrou obstáculo, então atualiza o mapa
        #if content[0] == 'O':
        #    position_list = content.split("X")[1].split("Y")
        #    map.put(int(position_list[0]), int(position_list[1]))
            #map_updated = True
	
        # TODO Avisar clientes da nova versão

	# Confirma recebimento correto
        request_response.response = 1
        
        print("Vou chamar update_msg")

        update_msg(content)

        return request_response


def update_msg(content = ''):
  global map, publisher_map_info #, node


  #publisher_map_data = node.create_publisher(GetMapData, '/map_data', 10) 
  

  map_info_msg = GetMapInfo()
  #map_data_msg = GetMapData()

  i = int(time.time())
  #TODO Mudar tipo de dado para mandar int logo
  #print("i = ", i)

  #map_info_msg.timestamp = '%d' % i
  map_info_msg.timestamp = str(i) + content
 # print("Vou publicar ", map_info_msg.timestamp)

  map_info_msg.width = map.width
  map_info_msg.height = map.height

#  node_publisher.publish(map_info_msg)

        
  #map_data_msg.data = map.content2str()
       
  #publisher_map_info.publish(map_info_msg)
  #publisher_map_data.publish(map_data_msg)

  publisher_map_info.publish(map_info_msg)

  map.show()
  print("Informação publicada: ", map_info_msg.timestamp)

def map_service():
  get_map_service = MapService('node_get_map', GetMapData, 'get_map_data')
  rclpy.spin(get_map_service)

def receive_msg_service():
  receive_msg_service = ReceiveMsgService('node_receive_msg', SendMsgServer, 'send_msg_server')
  rclpy.spin(receive_msg_service)
  print("Chamou receive msg")


def show_map():
  global map
  map.show()
  
# Função que trata o comando put
def put_obstacle(keyboard_input_list):
    print("Map before")
    show_map()
    x = int(keyboard_input_list[1])
    y = int(keyboard_input_list[2])
    print("Map after")
    show_map()
    
def check_update():
    if map_updated:
        update_msg()
    else:
        print("Sem atualizações, vou dormir um pouco")
        sleep(10.0)

def main(args=None):
    global node_publisher, node, publisher_map_info

    rclpy.init(args=args)

    show_map()

    node = rclpy.create_node('minimal_publisher')
    publisher_map_info = node.create_publisher(GetMapInfo, '/map_info', 10)

    #check_for_updates_thread = threading.Thread(target=check_update)
    #check_for_updates_thread.start()


    # Trecho do executador adaptado a partir daqui
    # https://robotics.stackexchange.com/questions/105877/node-keeps-crashing-due-to-valueerror-generator-already-executing
    try:
        executor = MultiThreadedExecutor()

        #node_publisher = MinimalPublisher()
        #executor.add_node(node_publisher)
        #node = rclpy.create_node('minimal_publisher')
        update_msg()
        executor.add_node(node)

        get_map_service = MapService('node_get_map', GetMapData, 'get_map_data')
        executor.add_node(get_map_service)
	
        receive_msg_service = ReceiveMsgService('node_receive_msg', SendMsgServer, 'send_msg_server')
        executor.add_node(receive_msg_service)

        try:
            executor.spin()
        except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
            executor.shutdown()
            #node_publisher.destroy_node()
            receive_msg_service.destroy_node()
            get_map_service.destroy_node()
        finally:
            executor.shutdown()
            #node_publisher.destroy_node()
            receive_msg_service.destroy_node()
            get_map_service.destroy_node()

    finally:
        node.destroy_node()
        rclpy.shutdown()


    

#    provide_map_service_thread = threading.Thread(target=map_service)
 #   provide_map_service_thread.start()

  #provide_receive_msg_service_thread = threading.Thread(target=receive_msg_service)
  #provide_receive_msg_service_thread.start()

 
  #  update_msg(node, map)
  
  # Mostre o mapa para conferir se o mesmo está sendo recebido
  # corretamente no cliente
  #  show_map()

#  command = ''
#  while command != 'exit':

#    keyboard_input = input('Digite um comando')
#    keyboard_input = keyboard_input.split()
#    command = keyboard_input[0]
#    
#    if command == 'put':
#      put_obstacle(keyboard_input)
#      
#    print(command)
      
   # while rclpy.ok():
    
    # Simula um padrão aleatório de alteração do mapa
#    rand_int = random.randint(0, 10)
#    print("Rand Int ", rand_int)    
#    if rand_int <= 1:
#      update_msg(node, map)    

    #    sleep(60.0)  # seconds

    print("Saindo do loop")

  # Encerra a thread que provê o mapa
    #provide_map_service_thread.join()
  
  # Encerra a thread que permite o envio de msgs pro servidor
  #provide_receive_msg_service_thread.join()

  # Destroy the node explicitly
  # (optional - otherwise it will be done automatically
  # when the garbage collector destroys the node object)
    #node.destroy_node()
    #rclpy.shutdown()

map = Map('/home/vinicius/s/doutorado/map.txt')
map_updated = True

if __name__ == '__main__':
  main()

