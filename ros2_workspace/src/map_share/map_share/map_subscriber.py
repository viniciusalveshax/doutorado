import rclpy
from rclpy.node import Node

#from std_msgs.msg import String
from map_interfaces.msg import GetMapInfo #, GetMapData
from map_interfaces.srv import GetMapData

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
        print(response.data)
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

def main(args=None):
    rclpy.init(args=args)

    sub1 = Subscriber('/map_info', map_info_callback)
    #sub2 = Subscriber('/map_data', map_info_callback)
    rclpy.spin(sub1)
    
    
    
    sub.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
    
last_timestamp = ""
