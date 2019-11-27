import pygame
import os
import neat
import random
import pickle
from datetime import datetime

pygame.init()

width = 760
height = 760
block_length = width/20
best_fitness = 0
button_w = block_length * 3
button_h = block_length * 2
max_moves = 150
local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, "config-feedforward.txt")
window = pygame.display.set_mode((width, height))
config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)


class Button:
    def __init__(self, color, x,y,width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.Font("Rentukka-Regular.otf", int(width/25))
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, (
            self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


class Apple:
    def __init__(self, snake, length=block_length, color=(255, 0, 0)):
        self.length = length
        self.color = color
        self.rand(snake)

    def rand(self, snake):
        rand_x = random.randint(0, width/self.length - 1) * self.length
        rand_y = random.randint(0, height/self.length - 1) * self.length
        if self.collide(snake, rand_x, rand_y):
            self.rand(snake)
        else:
            self.x = rand_x
            self.y = rand_y

    def collide(self, snake, rand_x, rand_y):
        for i in range(len(snake.snake_list)):
            if snake.snake_list[i].x == rand_x and \
                    snake.snake_list[i].y == rand_y:
                return True
        return False

    def run(self, snake):
        if snake.snake_list[0].x == self.x and snake.snake_list[0].y == self.y:
            self.rand(snake)
            snake.append()
            snake.moves += max_moves/2
            snake.fed = True
        pygame.draw.rect(window, self.color, (self.x, self.y, self.length, self.length))


class Snake:
    def __init__(self, num_node=3):
        self.snake_list = list()
        rand_index = random.randint(0, 3)
        rand_direction = [0, 0, 0, 0]
        rand_direction[rand_index] = 1
        self.snake_list.append(SnakeNode(width/2 - (width/2) % block_length,
                                        height/2 - (height/2) % block_length,
                                         rand_direction, (255, 255, 255)))
        self.apple = Apple(self)
        self.collision = False
        self.fed = False
        self.moves = max_moves

        for i in range(1,num_node):
            self.append()

    def dist(self):
        return ((self.snake_list[0].x - self.apple.x) ** 2 + (self.snake_list[0].y - self.apple.y) ** 2) ** 0.5

    def dist_x(self):
        return self.snake_list[0].x - self.apple.x

    def dist_y(self):
        return self.snake_list[0].y - self.apple.y

    def dist_left(self):
        dist = width
        for i in range(1, len(self.snake_list)):
            if self.snake_list[0].y == self.snake_list[i].y and \
                    0 < self.snake_list[0].x - self.snake_list[i].x < dist:
                dist = self.snake_list[0].x - self.snake_list[i].x - block_length
        if dist == width:
            dist = self.snake_list[0].x
        return dist

    def dist_right(self):
        dist = width
        for i in range(1, len(self.snake_list)):
            if self.snake_list[0].y == self.snake_list[i].y and \
                    0 < self.snake_list[i].x - self.snake_list[0].x < dist:
                dist = self.snake_list[i].x - self.snake_list[0].x - block_length
        if dist == width:
            dist = width - self.snake_list[0].x - block_length
        return dist

    def dist_top(self):
        dist = height
        for i in range(1, len(self.snake_list)):
            if self.snake_list[0].x == self.snake_list[i].x and \
                    0 < self.snake_list[0].y - self.snake_list[i].y < dist:
                dist = self.snake_list[0].y - self.snake_list[i].y - block_length
        if dist == height:
            dist = self.snake_list[0].y
        return dist

    def dist_bottom(self):
        dist = height
        for i in range(1, len(self.snake_list)):
            if self.snake_list[0].x == self.snake_list[i].x and \
                    0 < self.snake_list[i].y - self.snake_list[0].y < dist:
                dist = self.snake_list[i].y - self.snake_list[0].y - block_length
        if dist == height:
            dist = height - self.snake_list[0].y - block_length
        return dist

    def append(self):
        x = self.snake_list[-1].x
        y = self.snake_list[-1].y
        length = self.snake_list[-1].length
        if self.snake_list[-1].direction[0]:
            self.snake_list.append(SnakeNode(x+length, y, [1, 0, 0, 0]))
        elif self.snake_list[-1].direction[1]:
            self.snake_list.append(SnakeNode(x-length, y, [0, 1, 0, 0]))
        elif self.snake_list[-1].direction[2]:
            self.snake_list.append(SnakeNode(x, y+length, [0, 0, 1, 0]))
        elif self.snake_list[-1].direction[3]:
            self.snake_list.append(SnakeNode(x, y-length, [0, 0, 0, 1]))

    def input(self, direction):
        if direction == 0:
            if not self.snake_list[0].direction[1]:
                self.snake_list[0].change_direction(0)
        if direction == 1:
            if not self.snake_list[0].direction[0]:
                self.snake_list[0].change_direction(1)
        if direction == 2:
            if not self.snake_list[0].direction[3]:
                self.snake_list[0].change_direction(2)
        if direction == 3:
            if not self.snake_list[0].direction[2]:
                self.snake_list[0].change_direction(3)

        self.moves -= 1


    def run(self):
        temp = self.snake_list[0].direction.copy()
        for i in range(len(self.snake_list)):
            self.snake_list[i].run()
            if not self.collision:
                pygame.draw.rect(window, self.snake_list[i].color,
                                (self.snake_list[i].x, self.snake_list[i].y,
                                self.snake_list[i].length, self.snake_list[i].length))

            if i == 0:
                if self.snake_list[0].x < 0 or self.snake_list[0].x > width - self.snake_list[0].length \
                        or self.snake_list[0].y < 0 or self.snake_list[0].y > height - self.snake_list[0].length:
                    self.collision = True
            else:
                if self.snake_list[i].x == self.snake_list[0].x and \
                        self.snake_list[i].y == self.snake_list[0].y:
                    self.collision = True

                temp2 = self.snake_list[i].direction.copy()
                self.snake_list[i].direction = temp.copy()
                temp = temp2.copy()
        if not self.collision:
            self.apple.run(self)


class SnakeNode:
    def __init__(self, x=width/2, y=height/2, direction=list(), color=(180, 180, 180),
                 length=block_length, delta=block_length):
        self.x = x
        self.y = y
        self.length = length
        self.color = color
        self.delta = delta
        self.direction = direction

    def change_direction(self, new_direction):
        for i in range(4):
            if new_direction == i:
                self.direction[i] = True
            else:
                self.direction[i] = False

    def run(self):
        if self.direction[0]:
            self.x -= self.delta
        elif self.direction[1]:
            self.x += self.delta
        elif self.direction[2]:
            self.y -= self.delta
        elif self.direction[3]:
            self.y += self.delta


def save(genome):
    now = datetime.now()
    name = now.strftime("%d-%m-%Y_%H-%M-%S")
    name ="genomes/" + name + ".pickle"
    pickle.dump(genome, open(name, "wb"))


def eval_genome(genomes, config):
    back = Button((255, 255, 255), block_length,
                        block_length, button_w, button_h, "Return")

    snakes = []
    ge = []
    nets = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        snakes.append(Snake())
        g.fitness = 0
        ge.append(g)

    global best_fitness, best_g
    best_g = ge[0]

    running = True
    while running:
        window.fill((0,0,0))

        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                save(best_g)
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.isOver(pos):
                    best_g.fitness = 1100
            if event.type == pygame.MOUSEMOTION:
                if back.isOver(pos):
                    back.color = (200, 200, 200)
                else:
                    back.color = (255, 255, 255)

        for x, snake in enumerate(snakes):
            output = nets[x].activate((snake.dist(), snake.dist_x(),
                                        snake.dist_y(), snake.dist_left(),
                                        snake.dist_right(), snake.dist_top(),
                                        snake.dist_bottom()))

            direction = output.index(max(output))

            temp = snake.dist()

            snake.input(direction)
            snake.run()

            """if temp - snake.dist() > 0:
                ge[x].fitness += 0.5
            else:
                ge[x].fitness -= 1"""

            if ge[x].fitness >= best_fitness:
                best_fitness = ge[x].fitness
                best_g = ge[x]

            if snake.fed:
                ge[x].fitness += 10
                snake.fed = False

            if snake.collision or snake.moves < 0:
                ge[x].fitness -= 10
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)

            """for g in ge:
                g.fitness += 0.001"""

        if len(snakes) == 0:
            running = False
            break

        back.draw(window)
        #pygame.time.delay(50)
        pygame.display.update()
    print("Best fitness: " + str(best_fitness))


def train():
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genome, 200)
    save(winner)
    home()


def play():
    snake = Snake(3)
    running = True
    while running:
        window.fill((0, 0, 0))
        snake.run()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not snake.snake_list[0].direction[1]:
                        snake.snake_list[0].change_direction(0)
                if event.key == pygame.K_RIGHT:
                    if not snake.snake_list[0].direction[0]:
                        snake.snake_list[0].change_direction(1)
                if event.key == pygame.K_UP:
                    if not snake.snake_list[0].direction[3]:
                        snake.snake_list[0].change_direction(2)
                if event.key == pygame.K_DOWN:
                    if not snake.snake_list[0].direction[2]:
                        snake.snake_list[0].change_direction(3)
        if snake.collision:
            running = False
        pygame.time.delay(65)
        pygame.display.update()
    home()


def test():
    back = Button((255, 255, 255), block_length,
                  block_length, button_w, button_h, "Return")
    genome = pickle.load(open("best.pickle", "rb"))
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    snake = Snake()
    running = True
    while running:
        window.fill((0,0,0))
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.isOver(pos):
                    running = False
            if event.type == pygame.MOUSEMOTION:
                if back.isOver(pos):
                    back.color = (200, 200, 200)
                else:
                    back.color = (255, 255, 255)

        """output = net.activate((snake.dist(), snake.dist_x(), snake.dist_y(),
                               snake.dist_left(), snake.dist_right(),
                               snake.dist_top(), snake.dist_bottom()))"""

        output = net.activate((snake.dist(), snake.dist_x(), snake.dist_y(),
                               snake.dist_left(), snake.dist_right(),
                               snake.dist_top(), snake.dist_bottom()))

        direction = output.index(max(output))
        snake.input(direction)
        snake.run()
        back.draw(window)

        if snake.collision:
            running = False

        pygame.time.delay(40)

        pygame.display.update()
    home()


def home():

    button_train = Button((255, 255, 255), (width - button_w) / 2,
                        (height - button_h) / 2, button_w, button_h, "Train")
    button_test = Button((255, 255, 255), (width - button_w) / 2,
                        (height + button_h * 2) / 2, button_w, button_h, "Test")
    button_play = Button((255, 255, 255), (width - button_w) / 2,
                        (height + button_h * 5) / 2, button_w, button_h, "Play")

    running = True
    while running:
        window.fill((0, 0, 0))
        font = pygame.font.Font("Rentukka-Regular.otf", int(width/5))
        text = font.render("SnAIk", 1, (255, 255, 255))
        window.blit(text,
                    ((width / 2 - text.get_width() / 2), text.get_height()/2))

        button_train.draw(window)
        button_test.draw(window)
        button_play.draw(window)
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_train.isOver(pos):
                    running = False
                    train()
                elif button_test.isOver(pos):
                    running = False
                    test()
                elif button_play.isOver(pos):
                    running = False
                    play()

            if event.type == pygame.MOUSEMOTION:
                if button_train.isOver(pos):
                    button_train.color = (200, 200, 200)
                elif button_test.isOver(pos):
                    button_test.color = (200, 200, 200)
                elif button_play.isOver(pos):
                    button_play.color = (200, 200, 200)
                else:
                    button_train.color = (255, 255, 255)
                    button_test.color = (255, 255, 255)
                    button_play.color = (255, 255, 255)
        pygame.display.update()


if __name__ == "__main__":
    home()
