import pygame
from pygame.locals import *
from time import sleep
from math import sqrt, ceil, floor
from random import random
from maze import *

run = 1
size = (500, 500)
vtax = 1

def create_maze(grid):
    grid.reset(surface, 1)
    atualmaze = maze(99, 99)
    for x, i in enumerate(atualmaze):
        for y, j in enumerate(i):
            if j:
                grid.walls.append((x,y))
    grid.setwalls([])

def genetic_solve(surface, grid):
    next = []
    time = 20
    while run:
        mini = None
        results = []
        for i in range(time):
            b = [random() * 10,random() * 10,random() * 10,random() * 10]
            score = grid.solve(surface, b, mini)
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
            score = grid.solve(surface, val, mini)
            if mini == None or mini > score[1]: mini = score[1]
            grid.reset(surface)
            results.append([b, score])
        next = sorted(results, key = lambda x: x[1][0] * 2 + x[1][1])[:3]
        print next
        print "##############################################"
        next = [x[0] for x in next]
        create_maze(grid)
        time = 1

def events(grid):
    print("""e - Find a route
m - Create a Maze
r - Clear the screen""")
    grid.draw(surface)
    global run
    last = None
    to_remove = []
    while run:
        e = pygame.event.wait()
        if e.type == 6:
            last = None
        elif (e.type == 5 and e.button == 1) or (e.type == 4 and e.buttons[0]):
            pos = (int(ceil(e.pos[0] / float(size[0]) * grid.x)) - 1, int(round(e.pos[1] / float(size[1]) * grid.x)) - 1)
            to_remove = []
            if pos == last:
                continue
            else:
                last = pos
            if not pos in grid.walls:
                grid.walls.append(pos)
            else:
                to_remove.append(pos)
            grid.setwalls(to_remove)
            grid.draw(surface, 1)
        elif e.type == 2 and e.key == 101:
            grid.reset(surface)
            #genetic_solve(surface, grid)
            grid.solve(surface, [14, 10, 2, 2, 1], None)
        elif e.type == 2 and e.unicode == 'm':
            create_maze(grid)
            grid.draw(surface, 1)
        elif e.type == 2 and e.unicode == 'r':
            grid.reset(surface, 1)
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
            pygame.draw.rect(surface, (100, 100, 100), (self.x * 5, self.y * 5, 5, 5))
            #pygame.draw.rect(surface, (255, 255, 255), (self.x * 5, self.y * 5, 5, 5), 1)
            return
        if c == 1:
            pygame.draw.rect(surface, (0, 255, 0), (self.x * 5, self.y * 5, 5, 5))
            #pygame.draw.rect(surface, (255, 255, 255), (self.x * 5, self.y * 5, 5, 5), 1)
        elif c == 0:
            pygame.draw.rect(surface, (255, 0, 0), (self.x * 5, self.y * 5, 5, 5))
            #pygame.draw.rect(surface, (255, 255, 255), (self.x * 5, self.y * 5, 5, 5), 1)
        elif c == 2:
            pygame.draw.rect(surface, (0, 255, 0), (self.x * 5, self.y * 5, 5, 5))
            #pygame.draw.rect(surface, (0, 0, 0), (self.x * 5, self.y * 5, 5, 5), 1)

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
        pygame.draw.rect(surface, (255, 0, 255), (self.i[0] * 5, self.i[1] * 5, 5, 5))
        #pygame.draw.rect(surface, (255, 255, 255), (self.i[0] * 2, self.i[1] * 2, 2, 2), 1)
        #Draw the final block
        pygame.draw.rect(surface, (0, 0, 255), (self.f[0] * 5, self.f[1] * 5, 5, 5))
        #pygame.draw.rect(surface, (255, 255, 255), (self.f[0] * 2, self.f[1] * 2, 2, 2), 1)
        pygame.display.flip()

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
                    b = self.mesh[min(max(pos[0] + i, 0), self.x - 1)][min(max(pos[1] + j, 0), self.y - 1)]
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
            block = min(self.blocks, key = lambda i: i.d)
            block.draw(surface, 1)
            was.append(block)
            if limit != None and len(was) > limit * 2:
                return [1000, 1000]
            pos = (block.x, block.y)
            if block == aim: break
            if foi: break
        route = [self.mesh[self.f[0]][self.f[1]]]
        while 1:
            route.append(route[-1].dad)
            route[-1].draw(surface, 2)
            pygame.display.flip()
            if (route[-1].x, route[-1].y) == self.i: break
        #while 1:
        #    route.append(block)
        #    block = block.dad
        #    if block == None: break
        self.draw(surface, 1)
        for r in route:
            r.draw(surface, 2)
        pygame.display.flip()
        return [len(route),len(was)]
      
game = Grid(100, 100, [] , (1,1), (97, 97))
surface = pygame.display.set_mode(size)
events(game)
#game.solve(surface)

