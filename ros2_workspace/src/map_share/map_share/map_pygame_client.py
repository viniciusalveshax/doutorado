import pygame

# Bibliotecas do ROS2
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

# Para usar o sleep
from time import sleep

# Para lançar thread que lê o mapa inicialmente
import threading

# To use math.ceil
import math

from PIL import Image
import numpy as np

# Interfaces do ROS
from map_interfaces.msg import GetMapInfo #, GetMapData
from map_interfaces.srv import GetMapData, SendMsgServer

import sys
#TODO fazer isso dentro do padrão do ROS2
#sys.path.append('/home/vinicius/projetos/github/doutorado/ros2_workspace')

# Minhas classes e métodos
# Representação do mapa em modo texto
from map import Map
# Algoritmo do A*
from astar import AStar



#Determine if the neighboors are visible from a arbitrary point
def visible(tmp, x, y, scale):
	global img_np

	img_x_size, img_y_size, img_z_size = img_np.shape

	x = x * scale
	y = y * scale
	next_x = x + scale;
	next_y = y + scale;
	right_visible = True
	down_visible = True
	tmp_y = y
	if next_x >= img_x_size:
		next_x = img_x_size - 1
	if next_y >= img_y_size:
		next_y = img_y_size - 1	

	#print("NP x:", x, " y:", y, " valor:", img_np[x][y])

	while (tmp_y <= next_y):
		# Se encontrou uma parede na direita então o vizinho não é visível
		if np.array_equal(img_np[x][tmp_y], color_black):
			right_visible = False
			break
		tmp_y = tmp_y + 1
		#print("tmp y ", tmp_y)

	tmp_x = x
	while (tmp_x <= next_x):
		# Se encontrou uma parede abaixo então o vizinho não é visível
		if np.array_equal(img_np[tmp_x][y], color_black):
			down_visible = False
			break
		tmp_x = tmp_x + 1

	
	#if right_visible == False or down_visible == False:
	#	print("R IV, D IV", right_visible, down_visible)
	
	return down_visible, right_visible

#Generate and return a minimap create from original map
def generate_minimap(img_np, scale):
	img_x_size, img_y_size, img_z_size = img_np.shape

	# Minimap tem tamanho dobrado pois é necessário salvar a informação se os
	# pilares conseguem ver-se mutuamente
	minimap_x_data = math.ceil(img_x_size/scale)
	minimap_x_size = minimap_x_data * 2
	minimap_y_data = math.ceil(img_y_size/scale)
	minimap_y_size = minimap_y_data * 2

	# Cria uma matriz de amostragem
	minimap = np.ones((minimap_x_size, minimap_y_size, img_z_size))

	light_grey = (150, 150, 150)
	dark_grey = (50, 50, 50)

	x = 0
	y = 0		
	while x < minimap_x_data:
		while y < minimap_y_data:
			#print("X, y", x, y, x*scale, y*scale, minimap_x_size, minimap_y_size)
			minimap[x*2][y*2] = img_np[x*scale][y*scale]
			#print("Color minimap", minimap[x*2][y*2])
			right, down = visible(img_np, x, y, scale)
			if right:
				minimap[(x*2)+1][y*2] = np.array(light_grey)
			else:
				minimap[(x*2)+1][y*2] = np.array(dark_grey)
			if down:
				minimap[x*2][(y*2)+1] = np.array(light_grey)
			else:
				minimap[x*2][(y*2)+1] = np.array(dark_grey)

			minimap[(x*2)+1][(y*2)+1] = np.array(color_black)
			y = y + 1
		x = x + 1
		y = 0

	return minimap

def draw_line(point1, point2):
	global screen, surf, scale

	x1,y1 = point1
	x2,y2 = point2

	print("Desenhando reta de ", point1, " até ", point2)
	pygame.draw.line(screen, 'red', (x1*scale, y1*scale), (x2*scale, y2*scale), width = 3)
	#screen.blit(surf, (0, 0))


def draw_minimap_path(minimap_path):
	global scale

	resumed_path = []

	old_x = False
	old_y = False
	previous_direction = False

	for point in minimap_path:
		# Se é a primeira vez no loop só salva os valores pra próxima iteração
		if old_x == False:
			old_x, old_y = point
			continue
		else:
			# Se já não é a primeira vez então testa se algum dos pontos mudou
			new_x, new_y = point
			if new_x == old_x:
				direction = "horizontal"
			else:
				direction = "vertical"
			
			if direction != previous_direction:
				print(old_x, old_y)
				resumed_path.append((old_x*scale, old_y*scale))
			
			old_x, old_y = new_x, new_y
			previous_direction = direction


	last_point = minimap_path[-1]
	x_last_point, y_last_point = last_point

	resumed_path.append((x_last_point*scale, y_last_point*scale))
	
	if debug_level == 2:
		print(resumed_path)

	pygame.draw.lines(screen, 'red', False, resumed_path, width = 3)
	
	return resumed_path

def show_menu_options():
	print('q ou quit ou exit para sair')
	print('goto X Y para mover sem usar o minimap')
	print('gotomini X Y para mover usando o minimap')
	print('wasd para mover o agente')
	print('t ou y para testar a saída')
	print('h para repetir as opções')

def move_to_position(next_position):
	global x,y
	
	delta = 5

	next_x, next_y = next_position

	# Descubre se o movimento até a próxima posição é na horizontal ou na vertical	
	if x == next_x:
		delta_x = 0
		if y > next_y:
			delta_y = -delta
		else:
			delta_y = delta
	else:
		delta_y = 0
		if x > next_x:
			delta_x = -delta
		else:
			delta_x = delta
		
		
	
	while((x,y) != next_position):
		pygame.time.wait(500)
		
		reset_background()
#		draw_square(x, y, color_white)
		x = x + delta_x
		y = y + delta_y
		draw_red_square(x, y)

def reset_background():
	global img_np, start_background
	img_np = np.copy(start_background)

def follow_path(minimap_path):
	for position in minimap_path:
		move_to_position(position)

#Keyboard thread that read the keyboard and do something
def read_keyboard():
	global running, x, y, img_np

	while running == True:

		keyboard_input = input("Digite um comando. Digite 'h' para listar opções:")
		
		if keyboard_input == '' or keyboard_input == '\n':
			continue
			
		#keyboard_input = keyboard_input.strip()
		keyboard_input = keyboard_input.split()
		print(keyboard_input)

		if keyboard_input[0] == "q" or keyboard_input[0] == "quit" or keyboard_input[0] == "exit":
			running = False
		elif keyboard_input[0] == "w":
			print("x,y,size,dt:",x,y,size,dt)
			draw_red_square(x, y - size*dt)
		elif keyboard_input[0] == "s":
			draw_red_square(x, y + size*dt)
		elif keyboard_input[0] == "a":
			draw_red_square(x - size*dt, y)
		elif keyboard_input[0] == "d":
			draw_red_square(x + size*dt, y)
		elif keyboard_input[0] == 'h':
			show_menu_options()
		elif keyboard_input[0] == "goto":
			x_destination = keyboard_input[1]
			y_destination = keyboard_input[2]
			x_destination = int(x_destination)
			y_destination = int(y_destination)
			#print("Moving to x:", x_destination, ", y:", y_destination)

			#Draw path
			draw_destination(x_destination, y_destination)
			surf = pygame.surfarray.make_surface(img_np)
			screen.blit(surf, (0, 0))

			maze = AStar(map=img_np, start=(x, y), end=(x_destination, y_destination), debug=True)
			if maze.solve() == True:
				print("Foi possível resolver")
				#maze_path.print_map_with_solution()
				maze_path = maze.get_path()
				print(maze_path)
				draw_path(maze_path)
			else:
				print("Não foi possível resolver")

		# Goto on minimap
		elif keyboard_input[0] == "gotomini":
			x_destination = keyboard_input[1]
			y_destination = keyboard_input[2]
			x_destination = int(x_destination)
			y_destination = int(y_destination)
			x_dest_minimaze = int(x_destination/scale)
			y_dest_minimaze = int(y_destination/scale)						
		
			x_minimap = int(x/scale)
			y_minimap = int(y/scale)
		
			maze = AStar(map=minimap, start=(x_minimap, y_minimap), end=(x_dest_minimaze, y_dest_minimaze), debug=False)
			if maze.solve() == True:
				#maze_path.print_map_with_solution()
				maze_path = maze.get_path()
	
				# Se não adicionar a posição inicial não vai desenhar a última linha até o robô pois existe uma descontinuidade na amostragem
				maze_path = [(x_minimap, y_minimap)] + maze_path
				if debug_level==2:
					print("Foi possível resolver. Maze path: ", maze_path)
				draw_path(maze_path)
				resumed_path = draw_minimap_path(maze_path)
				
				follow_path(resumed_path)
			else:
				print("Não foi possível resolver")
		
		
		# Teste com quadrado cyano
		elif keyboard_input[0] == "t":
			img_np[1:100,1:100] = (0, 255, 255)
			#img_np[:, :, 3] = (255, 255, 0)
			surf = pygame.surfarray.make_surface(img_np)
			screen.blit(surf, (0, 0))
		# Teste com linhas vermelhas
		elif keyboard_input[0] == "y":
			img_np[:, ::3] = (255, 0, 255)
			surf = pygame.surfarray.make_surface(img_np)
			screen.blit(surf, (0, 0))

#Draw a possible path
def draw_path(path_list):
	global img_np
	tmp_size = 1
	for node in path_list:
		x, y = node
		img_np[x:x+tmp_size, y:y+tmp_size] = (0, 255, 0)
	surf = pygame.surfarray.make_surface(img_np)
	screen.blit(surf, (0, 0))
	


def draw_square(x, y, color):
	global img_np, size
	
	#Centraliza o robô
	x = int(x - size/2)
	y = int(y - size/2)

	img_np[x:x+size, y:y+size] = color


def draw_destination(x, y):
	global previous_x_destination, previous_y_destination, color_white, color_cyan
	#print(type(x), type(y))

	if previous_y_destination != -1:
		draw_square(previous_x_destination, previous_y_destination, color_white)

	draw_square(x, y, color_cyan)

	previous_x_destination = x
	previous_y_destination = y



def map_data_callback(msg):
    print("Mapa agora é ", msg.data)

def map_read():
    global shared_map, first_loading, minimal_client, executor
    debug(shared_map.version())

    debug("Lendo mapa")
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

class ClientWithOneParam(MinimalClientAsync):
    def send_request(self, a):
        self.req.a = a
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

def send_msg_to_server(msg):
    global client_with_param, executor
    future = client_with_param.send_request(msg)
    rclpy.spin_until_future_complete(client_with_param, future)
    debug("Requisição concluída")
    request_response = future.result()
    #minimal_client.get_logger().info(
    #    'Resultado %s' %
    #    (response.data))
    
    debug(request_response.response)
    
    #shared_map.set_content(response.data)

def notify_obstacle_to_server(position):
    # O -> Obstacle
    msg = 'OX' + str(position[0]) + 'Y' + str(position[1])
    debug("Encontrei obstáculo. Mandando msg: " + msg)
    send_msg_to_server(msg)
    
def follow_path(shared_map, planned_path):
    global position 

    # Enquanto houver caminho a ser percorrido
    while planned_path != []:
           
        # Pega a próxima posição
        next_position = planned_path[0]
        
        # Testa se a próxima posição está bloqueada
        if shared_map.get(next_position[0], next_position[1]) == '.':
            break

    	# Bota um símbolo _ na posição antiga
        shared_map.put(position[0], position[1], '_')        

	# Muda a posição            
        position = next_position
        
        # Muda o símbolo da próxima posição
        shared_map.put(position[0], position[1], '*')
        
        # Passa para a próxima posição do caminho e repete
        planned_path.pop(0)

        # Mostra o mapa e espera um tempo
        # (para a atualização não ser tão rápida)
        shared_map.show()
        sleep(2)
        

    if planned_path == []:  
        print("Cheguei")
    else:
        # Encontrei um obstáculo inesperado
        notify_obstacle_to_server(next_position)
        

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
    #menu()
   
def put(keyboard_input):
    global shared_map
    print("Função put")
    x = keyboard_input[1]
    y = keyboard_input[2]
    debug("Adicionando obstáculo no caminho do robô na posição x:"+x+", y:"+y)
   # shared_map.show()
    shared_map.put(int(x), int(y))
    shared_map.show()

def menu():
    print("Digite um comando")
    print("exit\ngoto X Y\nput X Y\nshow")
    keyboard_input = input('Digite um comando')
    return keyboard_input

def keyboard_reader():
    command = ''
    while command != 'exit':

        keyboard_input = menu()
        keyboard_input = keyboard_input.split()
        command = keyboard_input[0]
    
        if command == 'goto':
            #goto(keyboard_input)
            goto_thread = threading.Thread(target=goto, args=(keyboard_input,))
            goto_thread.start()
        elif command == 'put':
            put(keyboard_input)
        elif command == 'show':
            show_map()
      
        debug("Comando " + command)
    
    debug('Saindo do loop')
    #TODO Destruir nó e encerrar
    sys.exit()


def debug(msg):
  global debug_level
  if debug_level == 1:
    print(msg)


def draw_red_square(new_x, new_y):
	global x, y, color_white, color_red, img_np
	
	new_x = int(new_x)
	new_y = int(new_y)

	#Desenha um quadrado branco na posição anterior
	draw_square(x, y, color_white)
	
	#Redesenha o quadrado na posição atualizada
	if debug_level == 1:
		print("Drawing red square at x:", x, " y: ", y) 
	draw_square(new_x, new_y, color_red)

	surf = pygame.surfarray.make_surface(img_np)
	screen.blit(surf, (0, 0))

	#Atualiza as variáveis globais de posição
	x = new_x
	y = new_y

def pygame_window():
	global x, y, running, dt

	# Inicialização do Pygame
	pygame.init()

	#Faz o desenho inicial para não começar sem o quadrado
	draw_red_square(x, y)

	keyboard_reader_thread = threading.Thread(target=read_keyboard)
	keyboard_reader_thread.start()


	# Quanto deve ser a escala da amostragem do mapa para acelerar o A*?
	# Ex: Amostragem de 1:10 então scale=10
	scale = 20
	minimap = generate_minimap(img_np, scale)
	if debug_level == 2:
		print("Minimap array: ")
		print(minimap)
	surf = pygame.surfarray.make_surface(minimap)
	screen.blit(surf, (0, 0))

	x_minimap = int(x/scale)
	y_minimap = int(y/scale)
	print(minimap[x_minimap][y_minimap])

	print("x minimap ", x_minimap, " , y_minimap ", y_minimap)

	

	#print(img_np.shape, minimap.shape)
	#print(img_np[0][0], minimap[0][0])
	data = Image.fromarray(minimap.astype(np.uint8)) 
	data.save('minimap.bmp') 

	while running:
		# poll for events
		# pygame.QUIT event means the user clicked X to close your window
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
			    running = False

		# fill the screen with a color to wipe away anything from last frame
	#	screen.fill("green")

		#position = pygame.Vector2(x, y)
		
		# flip() the display to put your work on screen
		pygame.display.flip()

		# limits FPS to 60
		# dt is delta time in seconds since last frame, used for framerate-
		# independent physics.
		dt = clock.tick(10) / 1000
		
	keyboard_reader_thread.join()


	#print(img_np)

	# Encerra o programa
	pygame.quit()


def main(args=None):
	global executor, minimal_client, client_with_param
	
	setup_vars()

	# Inialização do ROS
	rclpy.init(args=args)

	pygame_window_thread = threading.Thread(target=pygame_window)
	pygame_window_thread.start()


	# Executador de múltiplas threads
	executor = MultiThreadedExecutor()

	# Nó para requisitar dados do mapa
	minimal_client = MinimalClientAsync('node_get_data', GetMapData, 'get_map_data')
	executor.add_node(minimal_client)

	# Nó para mandar mensagem para o servidor
	client_with_param = ClientWithOneParam('node_send_msg', SendMsgServer, 'send_msg_server')
	executor.add_node(client_with_param)

	# Primeira leitura do mapa
	map_read()

	sub1 = Subscriber('/map_info', map_info_callback)
	#sub2 = Subscriber('/map_data', map_info_callback)
	#rclpy.spin(sub1)

	executor.add_node(sub1)
	executor.spin()

	sub1.destroy_node()    
	minimal_client.destroy_node()
	client_with_param.destroy_node()
	pygame_window_thread.join()
	executor.shutdown()
	rclpy.shutdown()

	# Encerra a thread que lê o mapa
	#map_reader_thread.join()

def setup_vars():
	global x, y, shared_map, debug_level, position, color_white, color_red, color_cyan, color_black, screen, clock, running, dt, size, img, img_np, start_background, surf, pxarray, paused, previous_x_destination, previous_y_destination

	# 0: none, 1: minimal, 2: maximal
	debug_level = 1

	# Configura algumas cores comuns
	color_red = (255, 0, 0)
	color_white = (255, 255, 255)
	color_cyan = (0, 255, 255)
	color_black = (0, 0, 0)

	screen = pygame.display.set_mode((720, 720))
	clock = pygame.time.Clock()
	running = True
	dt = 0

	# Tamanho padrão do "robô"
	size = 30

	# Define a posição do robô na tela 
	x = int(screen.get_width() / 2)
	y = int(screen.get_height() / 2)

	# Lê o arquivo bmp e converte para numpy
	img = Image.open("/home/vinicius/s/doutorado/map.bmp")
	img_np = np.array(img)
	start_background = np.copy(img_np)

	#Mostra o objeto numpy
	surf = pygame.surfarray.make_surface(img_np)
	screen.blit(surf, (0, 0))

	#Converte to pixel array para manipulação direta
	pxarray = pygame.PixelArray(surf)

	#Inicialmente o programa não está pausado
	paused = False

	#Indica que inicialmente a localização do destino é inválida (não desenhar sobre a posição antiga)
	previous_x_destination = -1
	previous_y_destination = -1

	last_timestamp = ""
	debug_level = 1
	shared_map = Map('/home/vinicius/s/doutorado/map.txt')
	starting_position = (10, 10)
	position = starting_position
	first_loading = True

if __name__ == '__main__':
	main()
    

