import rclpy
from rclpy.node import Node

# Para usar o sleep
from time import sleep

# Para lançar thread que lê o mapa inicialmente
import threading

#from std_msgs.msg import String
from map_interfaces.msg import GetMapInfo #, GetMapData
from map_interfaces.srv import GetMapData

# Importa a classe que armazena o mapa
#import sys
#TODO fazer isso dentro do padrão do ROS2
#sys.path.append('/home/vinicius/projetos/github/doutorado/ros2_workspace')
from map import Map
from astar import AStar

def map_data_callback(msg):
    print("Mapa agora é ", msg.data)


def map_read():
    global shared_map, first_loading
    debug(shared_map.version())
    
    debug("Lendo mapa")
    minimal_client = MinimalClientAsync()
    future = minimal_client.send_request()
    rclpy.spin_until_future_complete(minimal_client, future)
    debug("Requisição concluída")
    response = future.result()
    #minimal_client.get_logger().info(
    #    'Resultado %s' %
    #    (response.data))
        
    shared_map.set_content(response.data)
    #map.show()

    #if first_loading == True:
    shared_map.put(position[0], position[1], '*')
    #first_loading = False

    minimal_client.destroy_node()
    
    debug("Leu o mapa")


def map_info_callback(msg):
    global last_timestamp
    if msg.timestamp != last_timestamp:
        last_timestamp = msg.timestamp
        print("Timestamp mudou para", last_timestamp) 
        map_read()
#        minimal_client = MinimalClientAsync()
#        future = minimal_client.send_request()
#        rclpy.spin_until_future_complete(minimal_client, future)
#        response = future.result()
#        print("Aqui")
#        print(type(response.data))
#        #minimal_client.get_logger().info(response.data)
#        #print(response.data)
#        map_formated = ''.join(response.data)
#        print(map_formated)
#        minimal_client.destroy_node()



class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(GetMapData, 'get_map_data')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = GetMapData.Request()

    def send_request(self):
        #self.req.a = a
        #self.req.b = b
        return self.cli.call_async(self.req)


class Subscriber(Node):
    def __init__(self, topic_name, callback_function):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            GetMapInfo,
            topic_name,
            callback_function,
            10)
        self.subscription  # prevent unused variable warning

def follow_path(shared_map, planned_path):
    global position 

    while planned_path != []:
    
    	# Bota um símbolo _ na posição antiga
        shared_map.put(position[0], position[1], '_')
        
        # Pega a próxima posição
        position = planned_path[0]
        
        # Muda o símbolo da próxima posição
        shared_map.put(position[0], position[1], '*')
        
        # Mostra o mapa e espera um tempo
        # (para a atualização não ser tão rápida)
        shared_map.show()
        sleep(3)
        
        # Passa para a próxima posição do caminho e repete
        planned_path.pop(0)
        
    print("Cheguei")
        

def goto(keyboard_input):
    global shared_map, position
    debug("Função goto. Executando A*")
    x_dest = int(keyboard_input[1])
    y_dest = int(keyboard_input[2])
    print("Posição",position)
    maze = AStar(map=shared_map.content(), start=(position[0],position[1]), end=(x_dest, y_dest), debug=True)
    if maze.solve() == True:
        maze.print_map_with_solution()
        planned_path = maze.get_path()
        follow_path(shared_map, planned_path)
    else:
        debug("Mapa sem solução :(")
    
def show_map():
    global shared_map
    shared_map.show() 
   
def put(keyboard_input):
    global shared_map
    print("Função put")
    x = keyboard_input[1]
    y = keyboard_input[2]
    debug("Adicionando obstáculo no caminho do robô na posição x:"+x+", y:"+y)
    shared_map.show()
    shared_map.put(int(x), int(y))
    shared_map.show()

def keyboard_reader():
    command = ''
    while command != 'exit':

        keyboard_input = input('Digite um comando')
        keyboard_input = keyboard_input.split()
        command = keyboard_input[0]
    
        if command == 'goto':
            goto(keyboard_input)
        elif command == 'put':
            put(keyboard_input)
        elif command == 'show':
            show_map()
      
        debug("Comando " + command)
    
    debug('Saindo do loop')
    #TODO Destruir nó e encerrar

def debug(msg):
  global debug_level
  if debug_level == 1:
    print(msg)

def main(args=None):
    rclpy.init(args=args)

    #map_reader_thread = threading.Thread(target=map_read)
    #map_reader_thread.start()
    
    # Primeira leitura do mapa
    map_read()

    keyboard_reader_thread = threading.Thread(target=keyboard_reader)
    keyboard_reader_thread.start()

    sub1 = Subscriber('/map_info', map_info_callback)
    #sub2 = Subscriber('/map_data', map_info_callback)
    rclpy.spin(sub1)
    
    sub1.destroy_node()
    rclpy.shutdown()

    # Encerra a thread que lê o mapa
    #map_reader_thread.join()

    keyboard_reader_thread.join()

last_timestamp = ""
debug_level = 1
shared_map = Map('/home/vinicius/s/doutorado/map.txt')
starting_position = (10, 10)
position = starting_position
first_loading = True

if __name__ == '__main__':
    main()
    

