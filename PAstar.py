import pygame
from pygame.locals import *
from time import sleep
from math import sqrt, ceil, floor
from random import random, choice, randrange
from maze import *

run = 1
gridsize = (50, 50)
scale = 8
size = (gridsize[0] * scale, gridsize[1] * scale)
vtax = 1

def find_neighbors(pos, stride = 1):
    """ List neighbors *stride* units away in each cardinal direction """
    x, y = pos
    neighbors = [(x - stride, y),
                 (x + stride, y),
                 (x, y - stride),
                 (x, y + stride)]
    return [p for p in neighbors
            if p[0] >= 0 and p[0] < gridsize[0] and
               p[1] >= 0 and p[1] < gridsize[1]]

def create_maze(grid):
    grid.reset(surface, 1)
    actualmaze = maze(gridsize[0] - 1, gridsize[1] - 1)
    for x, i in enumerate(actualmaze):
        for y, j in enumerate(i):
            if j:
                grid.walls.append((x,y))
    grid.setwalls([])

def genetic_solve(surface, grid):
    next = []
    time = 20

    def solve_score(*args):
        route, was = grid.solve(*args)
        return len(route), len(was)

    while run:
        mini = None
        results = []
        for i in range(time):
            b = [random() * 10,random() * 10,random() * 10,random() * 10]
            score = solve_score(surface, b, mini)
            if mini == None or mini > score[1]: mini = score[1]
            grid.reset(surface, 0)
            results.append([b, score])
        new = next[:]
        for m in next:
            new.append([])
            for k in m:
                new[-1].append(k)
            new[-1][int(random() * len(new[-1]))] += max(vtax * (random() - 0.5), 0)
        for val in new:
            score = solve_score(surface, val, mini)
            if mini == None or mini > score[1]: mini = score[1]
            grid.reset(surface)
            results.append([b, score])
        next = sorted(results, key = lambda x: x[1][0] * 2 + x[1][1])[:3]
        print next
        print "##############################################"
        next = [x[0] for x in next]
        create_maze(grid)
        time = 1

def mutate(grid, route, was):
    """ Make a random interesting change.
    
    If the route was successful, interrupt the route so that the solver must go
    around.
    If there was no successful route, then connect an explored area to an
    unexplored area in an attempt to allow a possible solution.
    """
    if len(route) > 2:
        followed = [(block.x, block.y) for block in route[1:-1]]
        breakage = choice(followed)
        grid.break_pos(breakage)
    elif was:
        explored = [(block.x, block.y) for block in was
                    if (block.x % 2) and (block.y % 2)]
        while explored:
            pos = choice(explored)
            neighbors = find_neighbors(pos, 2)
            missing_neighbors = [p for p in neighbors if p not in explored]
            if missing_neighbors:
                new_neighbor = choice(missing_neighbors)
                if grid.connect(pos, new_neighbor):
                    break

def events(grid):
    print("""e - Find a route
m - Create a Maze
r - Clear the screen
g - Fix the maze to conform to a grid
x - Make a random change to the route""")
    grid.draw(surface)
    global run
    last = None
    route = []
    was = []
    to_remove = []

    while run:
        e = pygame.event.wait()
        if e.type == 6:
            last = None
        elif (e.type == 5 and e.button == 1) or (e.type == 4 and e.buttons[0]):
            pos = (int(ceil(e.pos[0] / float(size[0]) * grid.x)) - 1,
                   int(round(e.pos[1] / float(size[1]) * grid.x)) - 1)
            if pos == last:
                continue
            last = pos
            grid.toggle_pos(pos)
        elif e.type == 2 and e.key == 101:
            grid.reset(surface)
            route, was = grid.solve(surface, [14, 10, 2, 2, 1], None)
        elif e.type == 2 and e.unicode == 'm':
            create_maze(grid)
            grid.draw(surface, 1)
        elif e.type == 2 and e.unicode == 'r':
            grid.reset(surface, 1)
        elif e.type == 2 and e.unicode == 'g':
            grid.gridify()
        elif e.type == 2 and e.unicode == 'x':
            mutate(grid, route, was)
        elif e.type == QUIT:
            run = 0
            

class Block:
    def __init__(self, x, y, dad, w = False):
        self.x = x
        self.y = y
        self.dad = dad
        self.visited = False
        self.di = 10000
        self.df = None
        self.d = None
        self.w = w

    def get_value(self, p1, p2, values, diagonal = 0):
        if diagonal:
            self.di = self.dad.di + values[0]
        else:
            self.di = self.dad.di + values[1]
        self.df = (abs(self.x - p2[0]) ** values[2] + abs(self.y - p2[1]) ** values[2]) * values[3]
        #self.df = (abs(self.x - p2[0]) + abs(self.y - p2[1])) * 10
        self.d = self.di + self.df

    def draw(self, surface, c = 0):
        if self.w:
            pygame.draw.rect(surface, (100, 100, 100),
                             (self.x * scale, self.y * scale, scale, scale))
            return
        if c == 1:
            pygame.draw.rect(surface, (0, 255, 0),
                             (self.x * scale, self.y * scale, scale, scale))
        elif c == 0:
            pygame.draw.rect(surface, (255, 0, 0),
                             (self.x * scale, self.y * scale, scale, scale))
        elif c == 2:
            pygame.draw.rect(surface, (0, 255, 0),
                             (self.x * scale, self.y * scale, scale, scale))

class Grid:
    def __init__(self, x, y, walls, ini, fin):
        self.x = x
        self.y = y
        self.walls = walls
        self.blocks = []
        self.mesh = [[None for i in range(y)] for j in range(x)]
        for i in range(x):
            for j in range(y):
                self.mesh[i][j] = Block(i, j, None)
        self.setwalls()
        self.i = ini
        self.f = fin

    def setwalls(self, rlist = []):
        for i in self.walls:
            self.mesh[i[0]][i[1]].w = True
        for i in rlist:
            self.mesh[i[0]][i[1]].w = False
            self.walls.remove(i)

    def reset(self, surface, walls = False):
        self.blocks = []
        if walls:
            self.walls = []
        for i in range(self.x):
            for j in range(self.y):
                self.mesh[i][j] = Block(i, j, None)
        self.setwalls()
        self.draw(surface, 1)
        pygame.display.flip()

    def draw(self, surface, init = 0):
        if init == 1:
            surface.fill((0,0,0))
            for i in self.walls:
                self.mesh[i[0]][i[1]].draw(surface)
        for b in self.blocks:
            b.draw(surface)
        #Draw the initial block
        pygame.draw.rect(surface, (255, 0, 255), (self.i[0] * scale, self.i[1] * scale, scale, scale))
        #pygame.draw.rect(surface, (255, 255, 255), (self.i[0] * 2, self.i[1] * 2, 2, 2), 1)
        #Draw the final block
        pygame.draw.rect(surface, (0, 0, 255), (self.f[0] * scale, self.f[1] * scale, scale, scale))
        #pygame.draw.rect(surface, (255, 255, 255), (self.f[0] * 2, self.f[1] * 2, 2, 2), 1)
        pygame.display.flip()

    def toggle_pos(self, pos):
        """ Toggle wall at pos """
        to_remove = []
        if not pos in self.walls:
            self.walls.append(pos)
        else:
            to_remove.append(pos)
        self.setwalls(to_remove)
        self.draw(surface, 1)

    def connect(self, a, b):
        """ Connect position a to position B, highlighting it on the grid """
        made_change = False
        for i in range(a[0], b[0] + 1):
            for j in range(a[1], b[1] + 1):
                if (i, j) in self.walls:
                    made_change = True
                    self.toggle_pos((i, j))

        if made_change:
            for i in range(a[0], b[0] + 1):
                for j in range(a[1], b[1] + 1):
                    Block(i, j, None).draw(surface, 1)
            
            pygame.display.flip()

        return made_change

    def break_pos(self, pos):
        """ Break the path at pos, and highlight the change on the display """
        neighbors = find_neighbors(pos)
        neighborhood = [pos] + neighbors
        for p in neighborhood:
            if p not in self.walls:
                self.toggle_pos(p)
        for p in neighborhood:
            self.gridify_pos(p)

        for p in neighborhood:
            Block(p[0], p[1], None).draw(surface, 1)
        
        pygame.display.flip()

    def gridify_pos(self, pos):
        """ Fix this position to consist with the maze grid """
        i, j = pos
        if not (i % 2) and not (j % 2) and not (pos in self.walls):
            self.toggle_pos(pos)
        if (i % 2) and (j % 2):
            neighbors = find_neighbors(pos)
            neighborhood = [pos] + neighbors
            neighbor_count = sum(
                1 if p in self.walls else 0 for p in neighbors)
            if neighbor_count == 4:
                # This square is completely unreachable, which is boring. It
                # also makes the 'x' command clunky to have single unreachable
                # squares because it wastes time connecting those instead of
                # connecting new areas.
                if pos in self.walls:
                    self.toggle_pos(pos)
                self.toggle_pos(choice(neighbors))
            else: # If it could be reachable it shouldn't be a wall
                if pos in self.walls:
                    self.toggle_pos(pos)

    def gridify(self):
        # Make the maze more griddy
        for i in range(gridsize[0]):
            for j in range(gridsize[1]):
                self.gridify_pos((i, j))

    def solve(self, surface, values, limit):
        block = self.mesh[self.i[0]][self.i[1]]
        pos = block.x, block.y
        block.visited = True
        block.di = 0
        aim = self.mesh[self.f[0]][self.f[1]]
        block.draw(surface, 1)
        was = [block]
        wasblocks = [block]
        counter = 0
        foi = 0
        while 1:
            counter += 1
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if (i == 0 and j == 0): continue
                    b = self.mesh[min(max(pos[0] + i, 0), self.x - 1)] \
                                 [min(max(pos[1] + j, 0), self.y - 1)]
                    if b.w: continue
                    if b in was: continue
                    if (b.x, b.y) == self.f: foi = 1
                    b.dad = block
                    if(abs(i + j) != 1):
                        b.get_value(self.i, self.f, values, 1)
                    else:
                        b.get_value(self.i, self.f, values)
                    if not b in self.blocks:
                        self.blocks.append(b)
                    block.visited = True
            self.draw(surface)
            if block in self.blocks:
                self.blocks.remove(block)
            wasblocks += self.blocks
            if (self.blocks):
                block = min(self.blocks, key = lambda i: i.d)
            else:
                return [[], was]
            block.draw(surface, 1)
            was.append(block)
            if limit != None and len(was) > limit * 2:
                return [[], was]
            pos = (block.x, block.y)
            if block == aim: break
            if foi: break
        route = [self.mesh[self.f[0]][self.f[1]]]
        while 1:
            route.append(route[-1].dad)
            route[-1].draw(surface, 2)
            pygame.display.flip()
            if (route[-1].x, route[-1].y) == self.i: break
        self.draw(surface, 1)
        for r in route:
            r.draw(surface, 2)
        pygame.display.flip()
        return (route, was)
      
game = Grid(gridsize[0], gridsize[1],
            [],
            (3,3),
            (gridsize[0] - 3, gridsize[1] - 3))
surface = pygame.display.set_mode(size)
events(game)
