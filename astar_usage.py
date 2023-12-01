from astar import AStar

map_file = open('map.txt', 'r')
    
# Inside rooms    
start = (3, 6)
end = (7, 35)

problem = AStar(map="map.txt", start=start, end=end)

#problem.print_map()

# Return true if there is a path
if problem.solve() == True:
	print("Found a way")
	problem.print_map_with_solution()
	path_from_1_to_2 = problem.get_path()
else:
	print("There is no path between start and end")
	

