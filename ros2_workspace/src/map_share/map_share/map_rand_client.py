import sys

from map_interfaces.srv import GetRand
import rclpy
from rclpy.node import Node


class MinimalClientAsync(Node):

    def __init__(self):
        super().__init__('minimal_client_async')
        self.cli = self.create_client(GetRand, 'get_rand_int')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = GetRand.Request()

    def send_request(self):
        #self.req.a = a
        #self.req.b = b
        return self.cli.call_async(self.req)


def main():
    rclpy.init()

    minimal_client = MinimalClientAsync()
    future = minimal_client.send_request()
    rclpy.spin_until_future_complete(minimal_client, future)
    response = future.result()
    minimal_client.get_logger().info(
        'Número aleatório %d' %
        (response.number))

    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
