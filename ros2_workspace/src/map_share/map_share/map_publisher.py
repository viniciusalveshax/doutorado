#Base code from https://answers.ros.org/question/337870/ros2-how-do-i-publish-exactly-one-message/

from time import sleep

import rclpy
from rclpy.node import Node

# Somente para testes iniciais
import random

# Para gerar o timestamp
import time

# Para lançar serviço
import threading

from map_interfaces.msg import GetMapInfo
from map_interfaces.srv import GetMapData

# Importa a classe que armazena o mapa
import sys
#TODO fazer isso dentro do padrão do ROS2
sys.path.append('/home/vinicius/projetos/github/doutorado/ros2_workspace')
from map import Map

class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(GetMapData, 'get_map_data', self.get_map_data_callback)

    def get_map_data_callback(self, request, response):
        global map
        response.data = map.content()
        #self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))

        return response



def update_msg(node, map):

  publisher_map_info = node.create_publisher(GetMapInfo, '/map_info', 10)
  #publisher_map_data = node.create_publisher(GetMapData, '/map_data', 10) 

  map_info_msg = GetMapInfo()
  #map_data_msg = GetMapData()

  i = int(time.time())
  #TODO Mudar tipo de dado para mandar int logo
  map_info_msg.timestamp = '%d' % i
  map_info_msg.width = map.width
  map_info_msg.height = map.height
  print("Vou publicar ", map_info_msg.timestamp)
        
  #map_data_msg.data = map.content2str()
       
  publisher_map_info.publish(map_info_msg)
  #publisher_map_data.publish(map_data_msg)


def map_service():
  minimal_service = MinimalService()
  rclpy.spin(minimal_service)

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

def main(args=None):
  rclpy.init(args=args)

  node = rclpy.create_node('minimal_publisher')

  provide_map_service_thread = threading.Thread(target=map_service)
  provide_map_service_thread.start()
 
  update_msg(node, map)
  
  # Mostre o mapa para conferir se o mesmo está sendo recebido
  # corretamente no cliente
  show_map()

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
      
  while rclpy.ok():
    
    # Simula um padrão aleatório de alteração do mapa
#    rand_int = random.randint(0, 10)
#    print("Rand Int ", rand_int)    
#    if rand_int <= 1:
#      update_msg(node, map)    

    sleep(60.0)  # seconds

  print("Saindo do loop")

  # Encerra a thread que provê o mapa
  provide_map_service_thread.join()

  # Destroy the node explicitly
  # (optional - otherwise it will be done automatically
  # when the garbage collector destroys the node object)
  node.destroy_node()
  rclpy.shutdown()

map = Map('/home/vinicius/s/doutorado/map.txt')

if __name__ == '__main__':
  main()

