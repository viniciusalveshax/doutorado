
# Memory stored map
mmap = []

# Read initial map file
filemap = open("map2.txt", "r")
for line in filemap:
	mmap.append(line)
	
for memory_line in mmap:
	print(memory_line, end='')
