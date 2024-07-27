import rclpy
from rclpy.node import Node

# Para lançar thread que lê o mapa inicialmente
import threading

#from std_msgs.msg import String
from map_interfaces.msg import GetMapInfo #, GetMapData
from map_interfaces.srv import GetMapData

# Importa a classe que armazena o mapa
import sys
#TODO fazer isso dentro do padrão do ROS2
sys.path.append('/home/vinicius/projetos/github/doutorado/ros2_workspace')
from map import Map

def map_data_callback(msg):
    print("Mapa agora é ", msg.data)

def map_info_callback(msg):
    global last_timestamp
    if msg.timestamp != last_timestamp:
        last_timestamp = msg.timestamp
        print("Timestamp mudou para", last_timestamp) 
        minimal_client = MinimalClientAsync()
        future = minimal_client.send_request()
        rclpy.spin_until_future_complete(minimal_client, future)
        response = future.result()
        print("Aqui")
        print(type(response.data))
        #minimal_client.get_logger().info(response.data)
        #print(response.data)
        map_formated = ''.join(response.data)
        print(map_formated)
        minimal_client.destroy_node()



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

def map_read():
    map = Map('/home/vinicius/s/doutorado/map2.txt')
    
    print("Lendo mapa")
    minimal_client = MinimalClientAsync()
    future = minimal_client.send_request()
    rclpy.spin_until_future_complete(minimal_client, future)
    print("Requisição concluída")
    response = future.result()
    minimal_client.get_logger().info(
        'Resultado %s' %
        (response.data))
        
    map.set_content(response.data)
    map.show()

    minimal_client.destroy_node()
    
    print("Leu o mapa")

def main(args=None):
    rclpy.init(args=args)

    #map_reader_thread = threading.Thread(target=map_read)
    #map_reader_thread.start()


    sub1 = Subscriber('/map_info', map_info_callback)
    #sub2 = Subscriber('/map_data', map_info_callback)
    rclpy.spin(sub1)
    
    sub.destroy_node()
    rclpy.shutdown()

    # Encerra a thread que lê o mapa
    #map_reader_thread.join()



if __name__ == '__main__':
    main()
    
last_timestamp = ""
