#Base code from https://answers.ros.org/question/337870/ros2-how-do-i-publish-exactly-one-message/

from time import sleep

import rclpy
import random

from map_interfaces.msg import GetMapInfo

def main(args=None):
  rclpy.init(args=args)

  node = rclpy.create_node('minimal_publisher')

  publisher_map_info = node.create_publisher(GetMapInfo, '/map_info', 10)
 

  i = 0
  msg = GetMapInfo()
  while rclpy.ok():
    
    # Simula um padrão aleatório de publicação    
    rand_int = random.randint(0, 10)
    print("Rand Int ", rand_int)    
    if rand_int < 1:
        
        msg.timestamp = 'Hello World: %d' % i
        print("Vou publicar ", msg.timestamp)
        i += 1
        publisher_map_info.publish(msg)

    sleep(1.0)  # seconds

  # Destroy the node explicitly
  # (optional - otherwise it will be done automatically
  # when the garbage collector destroys the node object)
  node.destroy_node()
  rclpy.shutdown()

if __name__ == '__main__':
  main()

