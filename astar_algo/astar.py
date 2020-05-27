class Node():
    '''
    types:
    parent = Node object
    position = tuple
    g = int
    h = int
    f = int
    '''

    def __init__(self,parent,position):
        self.parent=parent
        self.position=position
        
        self.g=0
        self.h=0
        self.f=0

    def __eq__(self,other):
        return self.position==other.position

def find_adjacent(current_node):
    '''Takes in a Node object and returns the adjacents positions: [right,left,up,left,top left,bottom right,top right,bottom left]

    current_node (obj) -> (list of tuples)     
    '''
    adjacent_positions=[]
    adjacent_vectors=[(0,1),(1,0),(0,-1),(-1,0)]
    for vector in adjacent_vectors:
        adjacent_positions.append((current_node.position[0]+vector[0],current_node.position[1]+vector[1]))
    return adjacent_positions


def valid(node_position,maze):
    '''takes in tuple of (row,column) and checks if it is valid
    
    node_position (tup), maze (list of lists) -> (bool)
    '''
    if node_position[1] > (len(maze) - 1):
        return False
    
    if node_position[0] > (len(maze[0]) -1):
        return False

    if maze[node_position[1]][node_position[0]]!=0:
        return False
    
    if node_position[0] < 0 :
        return False
    
    if node_position[1] < 0:
        return False
    return True

    
def astar(maze,start,end):
    start_node= Node(parent=None,position=start)
    end_node=Node(parent=None,position=end)
    
    open_list=[start_node]
    closed_list=[]
    
    while open_list:
        current_node=open_list.pop(0)
        closed_list.append(current_node)

        if current_node.position==end_node.position:
            path=[]
            while current_node is not None:
                path.append(current_node.position)
                current_node=current_node.parent

            else:
                #print(path)
                if len(path)>1:
                    return path[-2]
                else:
                    return path[-1]

        else:
            #have to find adjacent nodes
            adjacent_positions=find_adjacent(current_node)

            possible_adjacent_positions=[]
            for node_position in adjacent_positions:
                if valid(node_position,maze):
                    possible_adjacent_positions.append(node_position)
                else:
                    continue
            #Loop through remaining positions
            for child_position in possible_adjacent_positions:
                child_node=Node(parent=current_node,position=child_position) #converting positions to nodes
                if child_node in closed_list: #check for backtracking
                    continue

                child_node.g=current_node.g+1
                child_node.h=abs(child_node.position[0]-current_node.position[0])+abs(child_node.position[1]-current_node.position[1])
                child_node.f=child_node.g+child_node.h
            
                if child_node in open_list:
                    if child_node.g>current_node.g:
                        continue    
                
                open_list.append(child_node)
                open_list=sorted(open_list,key=lambda x: x.f)

    else:
        return None


def create_maze(screen_width,screen_height):
    return [[0]*(screen_width//50) for i in range(screen_height//50)]
   
