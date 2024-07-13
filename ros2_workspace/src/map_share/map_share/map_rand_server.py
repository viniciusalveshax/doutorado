from map_interfaces.srv import GetRand

import rclpy
from rclpy.node import Node

import random

class MinimalService(Node):

    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(GetRand, 'add_two_ints', self.add_two_ints_callback)

    def add_two_ints_callback(self, request, response):
        #response.sum = request.a + request.b
        #self.get_logger().info('Incoming request\na: %d b: %d' % (request.a, request.b))

	# Retorna como resposta um número aleatório entre 0 e 99
        response.sum = random.randint(0, 99)

        return response


def main():
    rclpy.init()

    minimal_service = MinimalService()

    rclpy.spin(minimal_service)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
