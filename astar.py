class AStar:

	def __init__(self, map, start, end=(), marker='', type="position", debug=False):
		if (type == "position" and end == ()) or (type == "marker" and marker == ''):
			raise Exception("Invalid constructor params")
		self.map = []
		for line in map:
			map_line = []
			map_line = list(line)
			self.map.append(map_line)
		self.start = start
		self.end = end
		self.map_with_path = {}
		self.path = []
		self.debug_option = debug

	def debug(self, value, label=''):
		if self.debug_option == True:
			if label != '':
				print(label, value)
			else:
				print(value)

	def get_path(self):
		return self.path

	def print_map_with_solution(self):
		print("Map with solution:")
		if self.map_with_path == {}:
			return
		self.debug(self.path, label="Caminho dentro de print map")
		count_line = 0
		for line in self.map:
			count_column = 0
			for char in line:
				tmp_node = (count_line, count_column)
				if tmp_node in self.path:
					print('x', end="")
				else:
					print(char, end="")
				count_column = count_column + 1
			count_line = count_line + 1


	def print_map(self):
		print("Original:")
		for line in self.map:
			print(line[0:-1])

	def print_position(self, position):
		x, y = position[0], position[1]
		print(self.map[x][y])


	def heuristic(self, test_node):
		# Use the manhattan distance https://en.wikipedia.org/wiki/Taxicab_geometry
		dif_x = test_node[0] - self.end[0]
		dif_y = test_node[1] - self.end[1]
		distance = abs(dif_x) + abs(dif_y)
		return distance

	def test_neighbor(self, x, y):
		if 0 <= x < len(self.map):
			if 0 <= y < len(self.map[x]):
				if self.map[x][y] != '.' and self.map[x][y] != '=' and self.map[x][y] != '|':
					return True

	def get_neighbors(self, node):
		self.debug(node, label="Listando os vizinhos para ")
		x, y = node[0], node[1]
		neighbors = set()
		if self.test_neighbor(x-1, y):
	#		print("Entrou")
			neighbors = neighbors | {(x-1,y)}
		if self.test_neighbor(x+1, y):
	#		print("Entrou")
			neighbors = neighbors | {(x+1,y)}
		if self.test_neighbor(x, y-1):
	#		print("Entrou")
			neighbors = neighbors | {(x,y-1)}
		if self.test_neighbor(x, y+1):
	#		print("Entrou")
			neighbors = neighbors | {(x,y+1)}
		return neighbors
		

	def get_better(self, nodes_set):
		nodes_list = list(nodes_set)
		# If the list have only one candidate then he is the best possible
		if len(nodes_list) == 1:
			
			return nodes_list[0]
		else:
			# If there is many candidates then calculate a score for each then pick the best
			better_score = 1000000
			better_index = 0
			index = 0
			for node in nodes_list:
				tmp_score = self.heuristic(node)
				self.debug(tmp_score, label="score: ")
				if tmp_score < better_score:
					better_score = tmp_score
					better_index = index
				index = index + 1
			better_node = nodes_list[better_index]
			return better_node
		

	def solve(self):
		# Where to start searching
		to_visit = {self.start}
		
		# Visited set - Empty at beginning
		visited = set()
		
		# Dict where saved discovery order - Will be used to mount the final path
		parent = {}
		
		# To diferenciate if loop finish because there is no way (no candidates left) or if alreay found the end 
		found = False
		
		# repeat while there is candidates and not found a way yet
		while len(to_visit) > 0 and found == False:
			
			# Get better candidate for now
			better_choice = self.get_better(to_visit)
			self.debug(better_choice, label="Better choice")
			
			# Add candidate to visited list (to not return to him)
			visited = visited | {better_choice}
			self.debug(visited, label="Visitados")
			
			# Get neighbors of candidate
			neighbors = self.get_neighbors(better_choice)
			self.debug(neighbors, label="Vizinhos")
			
			for neighbor in neighbors:
				# If neighbor not was in parent list then save their parent
				if not neighbor in parent:
					parent[neighbor] = better_choice
			
			# If the destination is in the neighbors list then found the way. Exit with success
			if self.end in neighbors:
				found = True
			else:
				# Filter the neighbors and leave only the non visited
				non_visited_neighbors = neighbors - visited
				self.debug(non_visited_neighbors, label="Non visited neighbors")
				
				# Add the remaining neighbors to list of candidates
				to_visit = to_visit | non_visited_neighbors
				
				to_visit = to_visit - {better_choice}
				
			self.debug(to_visit, label="To visit")
			
			# End of while search loop

		# Mount the path of the solution if found a way in previous loop
		if found:
			self.path = []
			self.map_with_path = {}
			
			# Begin to remount from the end and continues until reach start	
			tmp_node = self.end
			count = 0
			while tmp_node != self.start:
				self.path.append(tmp_node)
				tmp_x = tmp_node[0]
				tmp_y = tmp_node[1]
				if not (tmp_x, tmp_y) in self.map_with_path:
					self.map_with_path[(tmp_x, tmp_y)] = 'x'
				self.debug(tmp_node, label="Pai")
				tmp_node = parent[tmp_node]
				count = count + 1

			# Reverse the list to start from original beginning
			self.path.reverse()			
			#path = tmp_path
			#print("Caminho", tmp_path.reverse())
			#print("Marcados com x", self.path)
			#self.print_map_with_solution()
			return True
		else:
			# Not found a path
			return False
	

