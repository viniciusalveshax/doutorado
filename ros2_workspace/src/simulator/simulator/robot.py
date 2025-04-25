# Bibliotecas do ROS2
import rclpy
from rclpy.node import Node

from map_interfaces.srv import GetMapData #, SendMsgServer


class MinimalClientAsync(Node):

	def __init__(self, node_name, server_interface_type, topic_name):
		super().__init__(node_name)
		#self.cli = self.create_client(GetMapData, 'get_map_data')
		self.cli = self.create_client(server_interface_type, topic_name)
		while not self.cli.wait_for_service(timeout_sec=1.0):
			self.get_logger().info('service not available, waiting again...')
		self.req = server_interface_type.Request()

	def send_request(self):
		#self.req.a = a
		#self.req.b = b
		return self.cli.call_async(self.req)

def main(args=None):

	# Inialização do ROS
	rclpy.init(args=args)

	# Executador de múltiplas threads
	#executor = MultiThreadedExecutor()

	# Nó para requisitar dados do mapa
	minimal_client = MinimalClientAsync('node_get_data', GetMapData, 'get_map_data')
	#executor.add_node(minimal_client)

	future_request = minimal_client.send_request()
	rclpy.spin_until_future_complete(minimal_client, future_request)
	print("Requisição concluída")
	request_response = future_request.result()
	print(request_response)



if __name__ == '__main__':
	main()

