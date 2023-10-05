# -- MAIN SIMULATION -- #

import pygame
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import time
from scipy.spatial import KDTree, distance

# Define some constants
WIDTH, HEIGHT = 1920, 1080
FOOD_SIZE = 3
BACTERIA_COUNT = 100
FOOD_COUNT = 50
SPAWN_INTERVAL = 500


# Initialize Pygame
pygame.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("simulation")

RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class Food:
    def __init__(self, x=None, y=None):
        if x is None:
            self.x = random.randint(0, WIDTH)
        else:
            self.x = x
        if y is None:
            self.y = random.randint(0, HEIGHT)
        else:
            self.y = y
        self.color = (0, 255, 0)  # Food is green
        self.eaten = False  # Food is not eaten when it's created

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), FOOD_SIZE)


class Bacteria:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.energy = 100  # Bacteria start with 100 energy
        
        # traits
        self.sight = 50  # Bacteria can see food within this range
        self.speed = 1 # Faster bacteria use more energy to move the same distance 
        self.size = 5 # Bigger bacteria can eat smaller ones

    def move(self, is_debug):
        if is_debug: pygame.draw.rect(screen, RED, (self.x - self.sight / 2, self.y - self.sight / 2, self.sight, self.sight), 1)

        # If there is food in sight, move towards the closest one
        if len(food_list) > 0:  
            food_in_sight = [food for food in food_list if distance.euclidean((self.x, self.y), (food.x, food.y)) < self.sight]
            if food_in_sight:  
                closest_food = min(food_in_sight, key=lambda food: distance.euclidean((self.x, self.y), (food.x, food.y)))
                dir_vector = [closest_food.x - self.x, closest_food.y - self.y]
                length = distance.euclidean((self.x, self.y), (closest_food.x, closest_food.y))
                if is_debug: pygame.draw.line(screen, YELLOW, (self.x, self.y), (closest_food.x, closest_food.y), 3)
                if length != 0:  
                    dir_vector = [i/length for i in dir_vector]
                self.x += dir_vector[0] * self.speed
                self.y += dir_vector[1] * self.speed
            else:  # If there is no food in sight, move randomly
                self.x += random.randint(-1, 1) * self.speed
                self.y += random.randint(-1, 1) * self.speed
        self.energy -= self.speed + self.sight//100  # Moving costs energy
        #print(self.speed + self.sight//100)


    def can_eat(self, other):
        return self.size > other.size

    def eat(self, food, bacteria):
        if isinstance(food, Food):
            if distance.euclidean((self.x, self.y), (food.x, food.y)) < FOOD_SIZE + self.size:
                self.energy += 50  # Eating food gives energy
                food.eaten = True  # Mark the food as eaten
        if isinstance(bacteria, Bacteria):
            if self.can_eat(bacteria) and distance.euclidean((self.x, self.y), (bacteria.x, bacteria.y)) < self.size:
                print("eat")
                self.energy += bacteria.energy  # Eating bacteria gives their energy
                bacteria.energy = 0  # The eaten bacteria loses all its energy


    def mutate(self):
        mutation_factor = random.uniform(0.5, 2)
        self.sight *= mutation_factor
        self.speed *= mutation_factor
        self.size *= mutation_factor
        
    def split(self):
        if self.energy >= 200:  # If the bacterium has enough energy to split
            #print("split")
            self.energy /= 2  # Half of the energy goes to the offspring
            offspring = Bacteria()
            offspring.x = self.x
            offspring.y = self.y
            offspring.energy = self.energy  # The offspring gets the other half of the energy
            offspring.color = self.color
            
            # Mutate the traits of the offspring
            offspring.mutate()
            
            return offspring

    def summon(self, x, y):
        offspring = Bacteria()
        offspring.x = x
        offspring.y = y
        offspring.energy = 100
        
        return offspring

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)


# Create a list of bacteria and food
bacteria_list = [Bacteria() for _ in range(BACTERIA_COUNT)]
food_list = [Food() for _ in range(FOOD_COUNT)]
food_tree = KDTree([(food.x, food.y) for food in food_list])  # Create a k-d tree from the food positions


population = []; generations = []; sight = []; speed = []; size = []
display_graph = False; debug = False

start_time = time.time()


last_spawn_time = 0


# Game loop
running = True
def gen_food(Food, cluster_x, cluster_y):
    return Food(cluster_x + random.randint(-50, 50), cluster_y + random.randint(-50, 50))

def graph(screen, population, generations, string, pos):
    fig, ax = plt.subplots()
    ax.plot(generations, population)
        
    ax.set_xlabel('Generation')
    ax.set_ylabel(string)

    canvas = agg.FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()

    surf = pygame.image.fromstring(raw_data, canvas.get_width_height(), "RGB")

    screen.blit(surf, (pos))
    return canvas

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print("click")
            bacteria.summon(mos_x, mos_y)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                display_graph = not display_graph
            if event.key == pygame.K_2:
                debug = not debug
            
    screen.fill((0, 0, 0))
    
    mos_x, mos_y = pygame.mouse.get_pos()

    new_bacteria_list = []
    for bacteria in bacteria_list:
        if len(food_list) > 0:  # Only move and eat if there is food available
            bacteria.move(debug)
            bacteria.draw()
            for food in food_list:
                bacteria.eat(food, bacteria)
        offspring = bacteria.split()  # Check if the bacterium splits
        if offspring is not None:
            new_bacteria_list.append(offspring)  # Add the offspring to the new list

    # Add the new bacteria to the list
    bacteria_list.extend(new_bacteria_list)

    # Remove eaten food
    food_list = [food for food in food_list if not food.eaten]

    # Remove dead bacteria
    bacteria_list = [bacteria for bacteria in bacteria_list if bacteria.energy > 0]

    for food in food_list:
        food.draw()
        
        

    current_time = pygame.time.get_ticks()
    if current_time - last_spawn_time > SPAWN_INTERVAL:
        # Spawn a cluster of food at a random location
        cluster_x = random.randint(0, WIDTH)
        cluster_y = random.randint(0, HEIGHT)
        for _ in range(random.randint(0, 15)):  # Spawn between 0 and 15 pieces of food in the cluster
            new_food = gen_food(Food, cluster_x, cluster_y)
            food_list.append(new_food)
        last_spawn_time = current_time
        
    population.append(len(bacteria_list))
    generations.append(time.time() - start_time)
    sight.append(bacteria.sight)
    speed.append(bacteria.speed)
    size.append(bacteria.size)
    
    if display_graph:
        canvas = graph(screen, population, generations, 'Population', (1280, 0))
        canvas = graph(screen, sight, generations, 'Sight', (1280, 600))
        canvas = graph(screen, speed, generations, 'Speed', (0, 0))
        canvas = graph(screen, size, generations, 'Size', (0, 600))
        
    pygame.display.flip()
    
    matplotlib.pyplot.close()

pygame.quit()
