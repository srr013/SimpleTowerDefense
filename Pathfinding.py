import Queue


def heuristic(a, b):
    '''Returns the absolute value difference between 2 points a and b'''
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def a_star_search(graph, start, goal):
    '''Implements the A* search algorithm
    Returns: came_from dict, cost_so_far
    Graph: the available space to move. Usually from GridWithWeights
    Start: the starting point of the unit (x,y)
    Goal: Unit's end point (x,y)'''
    frontier = Queue.PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far

def get_path(map, start, goal):
    '''This is the main function call in Pathfinding.py. See a_star_search for info.'''
    came_from, cost_so_far = a_star_search(map, start, goal)
    #draw_grid(map, width=1, point_to=came_from, start=start, goal=goal)
    #draw_grid(map, width=1, number=cost_so_far, start=start, goal=goal)
    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):
    '''Takes the variables output by a_star_search and produces a movelist. See a_star_search for variable info'''
    current = goal
    path = []

    while current != start:
        path.append(current)
        try:
            current = came_from[current]
        except KeyError:
            return "Path Blocked"

    path.append(start)
    path.reverse()

    x = 0
    direction = []
    while x < len(path)-1:
        if path[x][1] == path[x+1][1]:
            if path[x][0] < path[x+1][0]:
                direction.append('r')
            else:
                direction.append('l')
        if path[x][0] == path[x+1][0]:
            if path[x][1] < path [x+1][1]:
                direction.append('u')
            else:
                direction.append('d')
        x+=1
    direction.append('r')#last square will always be right

    y=0
    move = []
    move.append(path[y])
    y+=1
    while y < len(direction):
        if y == len(direction)-1:
            move.append(path[y])
            break
        if direction[y-1] == direction[y]:
            pass
        else:
            move.append(path[y])
        y+=1

    return path, direction, move


class MapGrid():
    def __init__(self, width, height, border):
        '''Creates a basic grid for use in pathfinding algorithms.
        Width: the width of the available space to move
        Height: the height of the available spave to move
        border: a list of points that are impassable'''
        self.width = width - (border*2)
        self.height = height - (border*2)
        self.border = border
        self.walls = []

    def in_bounds(self, id):
        '''Used to ensure a unit doesn't move outside the boundaries'''
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id):
        '''Used to ensure a unit doesn't move through a wall'''
        return id not in self.walls

    def neighbors(self, id):
        '''Find neighboring spaces that the unit can move to'''
        (x, y) = id
        results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]#(x + 1,y + 1), (x + 1, y - 1), (x - 1,y - 1), (x - 1, y + 1)
        if (x + y) % 2 == 0: results.reverse()  # aesthetics
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results

class GridWithWeights(MapGrid):
    '''Creates a MapGrid then adds weight to each square to indicate the best route'''
    def __init__(self, width, height, border, goal):
        MapGrid.__init__(self,width, height, border)
        self.goal=goal
        self.weights = self.genWeights()


    def genWeights(self):
        weights = {}
        y_weight = 0
        x_weight = 0
        #weighting prefers movement closer to the base X coord over Y coord.
        for x in range(0,int(self.width)):
            if x + 1 % self.goal[0] == 0:
                x_weight = 0
            else:
                x_weight = abs(self.goal[0] - x)*.1

            for y in range (0,int(self.height)):
                if y+1 % self.goal[1] == 0:
                    y_weight = 0
                else:
                    y_weight= abs(self.goal[1]- y)*.01
                weights[x, y] = round(x_weight, 1) + round(y_weight, 1)
        return weights


    def cost(self, from_node, to_node):
        '''Determines the best route based on grid weighting'''
        return self.weights.get(to_node, 1)

# utility functions for dealing with square grids
def from_id_width(id, width):
    return (id % width, id // width)

def draw_tile(graph, id, style, width):
    r = "."
    if 'number' in style and id in style['number']: r = "%d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = ">"
        if x2 == x1 - 1: r = "<"
        if y2 == y1 + 1: r = "v"
        if y2 == y1 - 1: r = "^"
    if 'start' in style and id == style['start']: r = "A"
    if 'goal' in style and id == style['goal']: r = "Z"
    if 'path' in style and id in style['path']: r = "@"
    if id in graph.walls: r = "#" * width
    return r

def draw_grid(graph, width=1, **style):
    for y in range(int(graph.height)):
        xlist = list()
        for x in range(int(graph.width)):
            xlist.append("%%-%ds" % width % draw_tile(graph, (x, y), style, width))
        print (xlist)
