import rclpy
from rclpy.node import Node

#from std_msgs.msg import String
from map_interfaces.msg import GetMapInfo

def map_info_callback(msg):
    global last_timestamp
    if msg.timestamp != last_timestamp:
        last_timestamp = msg.timestamp
        print("Timestamp mudou para ", last_timestamp) 

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

    sub = Subscriber('/map_info', map_info_callback)
    rclpy.spin(sub)
    
    sub.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
    
last_timestamp = ""
