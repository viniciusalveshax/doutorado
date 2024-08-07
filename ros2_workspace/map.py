import os

class Map:
  def __init__(self, file_path):

    self.file_content = []
    tmp_file = open(file_path, 'r')
    self.file_content = tmp_file.readlines()
    
    self.width = len(self.file_content[0])
    self.height = len(self.file_content)
    
  def content(self):
    return self.file_content
    
  def set_content(self, new_content):
    self.file_content = new_content
    return True
    
  def content2str(self):
    return ''.join(self.file_content)
    
  def width(self):
    return self.width
   
  def height(self):
    return self.height

  def show(self):
    for line in self.file_content:
      print(line, end='')
      
  def get(self, x, y):
    tmp_line = self.file_content[x]
    return tmp_line[y]
      
  def put(self, x, y, char = '.'):
    tmp_line = self.file_content[x]
    
    #https://stackoverflow.com/questions/41752946/replacing-a-character-from-a-certain-index
    tmp_line = tmp_line[:y] + char + tmp_line[y + 1:]
    
    self.file_content[x] = tmp_line
    
  def version(self):
    pwd = os.getcwd()
    return pwd + ", 1.1"

